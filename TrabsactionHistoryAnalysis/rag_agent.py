# rag_agent.py

import os
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import config # Your existing config file

# --- CONFIGURATION ---
TEXTBOOK_PATH = "rag_source/bayesian_data_analysis.pdf"
VECTOR_STORE_PATH = "rag_db"
EMBEDDING_MODEL_NAME = "text-embedding-004"

def format_docs(docs):
    """Helper function to format retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

class RAGAgent:
    """
    An agent dedicated to retrieving supplemental context from a textbook
    to inform the statistician's reasoning process.
    """
    def __init__(self):
        """Initializes the RAG agent by creating or loading the vector store."""
        print("--- Initializing RAG Agent ---")
        self._vector_store = self._create_or_load_vector_store()
        self.retriever = self._vector_store.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3 relevant chunks
        print("--- RAG Agent Initialized Successfully ---")

    def _create_or_load_vector_store(self):
        """
        Creates a new vector store from the textbook or loads an existing one.
        This is the INGESTION pipeline. It runs only if the database doesn't exist.
        """
        if os.path.exists(VECTOR_STORE_PATH):
            print(f"--- RAG: Loading existing vector store from '{VECTOR_STORE_PATH}' ---")
            embeddings = VertexAIEmbeddings(model_name=EMBEDDING_MODEL_NAME, project=config.PROJECT_ID)
            vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
            return vector_store
        else:
            print(f"--- RAG: No vector store found. Creating a new one from '{TEXTBOOK_PATH}' ---")
            
            # 1. Load the document
            print("RAG: Loading PDF...")
            loader = PyPDFLoader(TEXTBOOK_PATH)
            docs = loader.load()
            print(f"RAG: Loaded {len(docs)} pages from the book.")

            # 2. Split the document into chunks
            print("RAG: Splitting document into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            print(f"RAG: Document split into {len(splits)} chunks.")

            # 3. Create the embedding model
            print(f"RAG: Initializing embedding model '{EMBEDDING_MODEL_NAME}'...")
            embeddings = VertexAIEmbeddings(model_name=EMBEDDING_MODEL_NAME, project=config.PROJECT_ID)

            # 4. Ingest chunks into ChromaDB
            print("RAG: Ingesting chunks into ChromaDB. This may take a few minutes...")
            vector_store = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=VECTOR_STORE_PATH
            )
            print("--- RAG: Vector store created and persisted successfully. ---")
            return vector_store

    def retrieve_context(self, query: str) -> str:
        """
        Retrieves relevant context from the textbook based on a query.
        The query is expected to be the 'thought' process of the statistician.
        """
        print(f"--- RAG: Retrieving context for query: '{query[:80]}...' ---")
        if not query:
            return "No query was provided for context retrieval."
        
        retrieved_docs = self.retriever.invoke(query)
        formatted_context = format_docs(retrieved_docs)
        print("--- RAG: Context retrieval complete. ---")
        return formatted_context