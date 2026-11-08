import os
from dotenv import load_dotenv
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from a .env file
load_dotenv()


class LocalEmbeddings:
    """Free on-device embeddings using all-MiniLM-L6-v2 via ONNX."""
    def __init__(self):
        self.ef = embedding_functions.DefaultEmbeddingFunction()

    def embed_documents(self, texts):
        return self.ef(texts)

    def embed_query(self, text):
        return self.ef([text])[0]


RAG_SEARCH_PROMPT_TEMPLATE = """
Using the following pieces of retrieved context, answer the question comprehensively and concisely.
Ensure your response fully addresses the question based on the given context.

**IMPORTANT:**
Just provide the answer and never mention or refer to having access to the external context or information in your answer.
If you are unable to determine the answer from the provided context, state 'I don't know.'

Question: {question}
Context: {context}
"""

print("Loading & Chunking Docs...")
loader = TextLoader("./data/agency.txt")
docs = loader.load()

doc_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
doc_chunks = doc_splitter.split_documents(docs)

print("Creating local vector embeddings with all-MiniLM-L6-v2...")
embeddings = LocalEmbeddings()

vectorstore = Chroma.from_documents(doc_chunks, embeddings, persist_directory="db")

# Semantic vector search
vectorstore_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Test RAG chain
print("Testing RAG chain...")
prompt = ChatPromptTemplate.from_template(RAG_SEARCH_PROMPT_TEMPLATE)
model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
llm = ChatGroq(model_name=model_name, temperature=0.1)

rag_chain = (
    {"context": vectorstore_retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

query = "What are your pricing options?"
result = rag_chain.invoke(query)
print(f"Question: {query}")
print(f"Answer: {result}")
