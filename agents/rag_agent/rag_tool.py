import os
import openai
from typing import List
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain.tools import tool

# 🔐 Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

# 🧠 Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# 📌 Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# 🔎 Get OpenAI embedding
def get_query_embedding(query: str) -> List[float]:
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        return response.data[0].embedding
    except Exception as e:
        print("❌ Embedding error:", e)
        return []

# 🔍 Search Pinecone index
def retrieve_context_chunks(query: str, top_k: int = 10) -> str:
    embedding = get_query_embedding(query)
    if not embedding:
        return "❌ Failed to get query embedding."

    try:
        results = index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"source": {"$eq": "additional2"}}
        )
        chunks = [match["metadata"]["text"] for match in results.get("matches", [])]
        return "\n\n".join(chunks) if chunks else "No relevant context found."
    except Exception as e:
        print("❌ Pinecone query error:", e)
        return "❌ Pinecone retrieval failed."



# 🛠️ LangGraph-compatible tool

@tool
def vector_search(query: str) -> str:
    """Useful for retrieving relevant report context chunks for a given query from Pinecone."""
    print(f"🔎 [Vector Search Tool] Query received: {query}")
    return retrieve_context_chunks(query)

