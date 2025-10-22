# create_vector_store.py
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
import config

# --- Configuration ---
PDF_PATH = "rag_source/bayesian_data_analysis.pdf"
VECTOR_STORE_PATH = "faiss_index"

def main():
    print("--- 🚀 Initializing RAG Vector Store ---")

    if not os.path.exists(PDF_PATH):
        print(f"❌ Error: Source PDF not found at '{PDF_PATH}'")
        return

    # 1. Load the PDF using the robust PyMuPDF engine
    print(f"📄 Loading PDF from '{PDF_PATH}'...")
    loader = PyMuPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} pages from the PDF.")

    # 2. Split the document text into manageable chunks
    print("쪼개기 Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100
    )
    docs = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(docs)} text chunks.")

    # 3. Initialize the embedding model
    print("🧠 Initializing Vertex AI embedding model...")
    embeddings = VertexAIEmbeddings(
        model_name="text-embedding-004", 
        project=config.PROJECT_ID
    )

    # 4. Create and save the FAISS vector store
    print("💾 Creating and saving FAISS vector store... (This may take a moment)")
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"--- ✅ Vector store successfully created and saved to '{VECTOR_STORE_PATH}' ---")

if __name__ == "__main__":
    main()