# rag_agent.py
import os
import config
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
VECTOR_STORE_PATH = "faiss_index"

class RAGAgent:
    """An agent that performs Retrieval-Augmented Generation using a local FAISS vector store."""
    def __init__(self):
        print("--- 🚀 Initializing RAG Agent ---")
        if not os.path.exists(VECTOR_STORE_PATH):
            print(f"❌ Error: Vector store not found at '{VECTOR_STORE_PATH}'.")
            print("Please run 'create_vector_store.py' first.")
            raise FileNotFoundError(f"Vector store not found at '{VECTOR_STORE_PATH}'")

        # 1. Initialize the models (LLM and Embeddings)
        # The embedding model MUST match the one used to create the store.
        self.embeddings = VertexAIEmbeddings(
            model_name="text-embedding-004", 
            project=config.PROJECT_ID
        )
        self.llm = ChatVertexAI(
            project=config.PROJECT_ID, 
            model_name=config.MODEL_NAME
        )

        # 2. Load the local FAISS vector store
        print(f"📂 Loading vector store from '{VECTOR_STORE_PATH}'...")
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, self.embeddings, allow_dangerous_deserialization=True)
        self.retriever = vector_store.as_retriever()
        print("✅ Vector store loaded successfully.")

        # 3. Define the RAG prompt template
        template = """
        You are an expert on Bayesian data analysis. Answer the user's question based only on the following context.
        If the context doesn't contain the answer, state that you don't have enough information.

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        self.prompt = ChatPromptTemplate.from_template(template)

        # 4. Build the RAG chain using LangChain Expression Language (LCEL)
        self.rag_chain = (
            RunnableParallel(
                {"context": self.retriever, "question": RunnablePassthrough()}
            )
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        print("--- ✅ RAG Agent Initialized ---")

    def answer(self, query: str):
        """Answers a query using the RAG chain."""
        print(f"\n--- 🤔 Querying RAG Agent with: '{query}' ---")
        return self.rag_chain.invoke(query)

# --- Example Usage (for testing) ---
if __name__ == '__main__':
    try:
        rag_agent = RAGAgent()
        
        # Example query
        query = "What is the core idea of Bayesian inference?"
        result = rag_agent.answer(query)
        
        print("\n--- 🎓 RAG Agent's Answer ---")
        print(result)

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")