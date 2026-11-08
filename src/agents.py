import os
from chromadb.utils import embedding_functions
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from .config import settings
from .structure_outputs import (
    CategorizeEmailOutput,
    RAGQueriesOutput,
    WriterOutput,
    ProofReaderOutput,
)
from .prompts import (
    CATEGORIZE_EMAIL_PROMPT,
    GENERATE_RAG_QUERIES_PROMPT,
    GENERATE_RAG_ANSWER_PROMPT,
    EMAIL_WRITER_PROMPT,
    EMAIL_PROOFREADER_PROMPT,
)


class LocalEmbeddings:
    """Free, on-device local embeddings using all-MiniLM-L6-v2 via ONNX."""
    def __init__(self):
        self.ef = embedding_functions.DefaultEmbeddingFunction()

    def embed_documents(self, texts):
        return self.ef(texts)

    def embed_query(self, text):
        return self.ef([text])[0]


class Agents:
    def __init__(self):
        # Choose which LLMs to use (configurable via settings)
        llm = ChatGroq(model_name=settings.groq_model, temperature=settings.temperature, max_retries=6)

        # Chroma vectorstore with free local embeddings
        embeddings = LocalEmbeddings()
        vectorstore = Chroma(persist_directory="db", embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": settings.rag_k})

        # Categorize email chain
        cat_parser = PydanticOutputParser(pydantic_object=CategorizeEmailOutput)
        cat_prompt = PromptTemplate(
            template=(
                CATEGORIZE_EMAIL_PROMPT
                + "\n\nIMPORTANT: Return ONLY a valid JSON object matching this schema:\n{format_instructions}"
            ),
            input_variables=["email"],
            partial_variables={"format_instructions": cat_parser.get_format_instructions()},
        )
        self.categorize_email = cat_prompt | llm | cat_parser

        # Design queries for RAG retrieval
        query_parser = PydanticOutputParser(pydantic_object=RAGQueriesOutput)
        generate_query_prompt = PromptTemplate(
            template=(
                GENERATE_RAG_QUERIES_PROMPT
                + "\n\nIMPORTANT: Return ONLY a valid JSON object matching this schema:\n{format_instructions}"
            ),
            input_variables=["email"],
            partial_variables={"format_instructions": query_parser.get_format_instructions()},
        )
        self.design_rag_queries = generate_query_prompt | llm | query_parser

        # Generate answer to queries using RAG
        qa_prompt = ChatPromptTemplate.from_template(GENERATE_RAG_ANSWER_PROMPT)
        self.generate_rag_answer = (
            {"context": retriever, "question": RunnablePassthrough()}
            | qa_prompt
            | llm
            | StrOutputParser()
        )

        # Used to write a draft email based on category and related information
        writer_parser = PydanticOutputParser(pydantic_object=WriterOutput)
        system_writer = SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template=(
                    EMAIL_WRITER_PROMPT
                    + "\n\nIMPORTANT: Return ONLY a valid JSON object matching this schema:\n{format_instructions}"
                ),
                input_variables=[],
                partial_variables={"format_instructions": writer_parser.get_format_instructions()},
            )
        )
        writer_prompt = ChatPromptTemplate.from_messages(
            [
                system_writer,
                MessagesPlaceholder("history"),
                ("human", "{email_information}"),
            ]
        )
        self.email_writer = writer_prompt | llm | writer_parser

        # Verify the generated email
        proofreader_parser = PydanticOutputParser(pydantic_object=ProofReaderOutput)
        proofreader_prompt = PromptTemplate(
            template=(
                EMAIL_PROOFREADER_PROMPT
                + "\n\nIMPORTANT: Return ONLY a valid JSON object matching this schema:\n{format_instructions}"
            ),
            input_variables=["initial_email", "generated_email"],
            partial_variables={"format_instructions": proofreader_parser.get_format_instructions()},
        )
        self.email_proofreader = proofreader_prompt | llm | proofreader_parser
