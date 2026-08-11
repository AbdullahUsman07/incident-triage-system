import os 
from pathlib import Path 
from typing import List, Dict  
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "incident-triage")

class IncidentRetriever:
    """Retrieves top matching historical post-mortems from Pinecone from a given error log."""

    def __init__(self, top_k: int =3):
        self.top_k = top_k
        print("Loading Embedding Model for Retrieval...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Connecting to Pinecone Index...")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.index(INDEX_NAME)

    def search_similar_incidents(self, log_text: str) -> List[Dict]:
        """Converts incoming log text to vector and queries Pinecone for matches"""

        # Generate Embedding for query log
        query_vector = self.model.encode(log_text).tolist()

        # Query Pinecone Index
        response = self.index.query(  
            vector=query_vector,
            top_k=self.top_k,
            include_metadata=True
        )

        matches = []
        for match in response.get("matches", []):
            matches.append({
                "id": match["id"],
                "score": round(match["score"], 4),  # Cosine similarity score (0.0 to 1.0)
                "title": match["metadata"].get("title", "Unknown Title"),
                "company": match["metadata"].get("company", "Unknown"),
                "summary": match["metadata"].get("summary", ""),
                "text": match["metadata"].get("text", ""),
                "source": match["metadata"].get("source", "")
            })

        return matches


if __name__ == "__main__":
    retriever = IncidentRetriever(top_k=2)
    sample_log = "sqlalchemy.exc.OperationalError: FATAL: max_connections reached for user postgres"
    print(f"\n🔍 Searching vector store for query: '{sample_log}'\n")

    results = retriever.search_similar_incidents(sample_log)
    for idx, res in enumerate(results, 1):
        print(f"Match #{idx} (Score: {res['score']}): {res['title']}")
        print(f"   Company: {res['company']}")
        print(f"   Snippet: {res['text'][:120]}...\n")