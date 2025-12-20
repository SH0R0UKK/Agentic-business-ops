import chromadb
import logging
import os
from sentence_transformers import SentenceTransformer
from .models import ResearchResult

logger = logging.getLogger(__name__)

class LocalLibrarian:
    def __init__(self, persist_path="./backend/data/knowledge_base"):
        """
        persist_path: Where the vector DB files will be stored.
        """
        # Ensure directory exists
        os.makedirs(persist_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name="agent_memory")
        
        # Load embedding model (Free, runs on CPU)
        logger.info("📚 Loading local embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def search(self, query: str, threshold: float = 1.2) -> ResearchResult | None:
        """
        Searches local DB. 
        Threshold: Lower = stricter match. 1.2 is a balanced starting point.
        """
        try:
            query_vec = self.encoder.encode([query]).tolist()
            
            results = self.collection.query(
                query_embeddings=query_vec,
                n_results=1
            )

            # Check if we got any result
            if not results['documents'] or not results['documents'][0]:
                return None

            distance = results['distances'][0][0]
            
            if distance < threshold:
                doc_content = results['documents'][0][0]
                metadata = results['metadatas'][0][0]
                
                logger.info(f"✅ Found in local memory (Distance: {distance:.2f})")
                
                return ResearchResult(
                    summary=doc_content, 
                    key_statistics=["Retrieved from internal memory"],
                    citations=[metadata.get("source", "Internal Memory")],
                    confidence_score=10,
                    source_type="local"
                )
            
            return None

        except Exception as e:
            logger.warning(f"⚠️ Local search error: {e}")
            return None

    def save_memory(self, result: ResearchResult, query: str):
        """
        Saves a ResearchResult into the vector DB for future use.
        """
        text_representation = (
            f"Query: {query}\n"
            f"Summary: {result.summary}\n"
            f"Stats: {', '.join(result.key_statistics)}"
        )
        
        vector = self.encoder.encode([text_representation]).tolist()
        
        # Unique ID based on query hash to avoid duplicates
        doc_id = f"mem_{hash(query)}"
        
        self.collection.upsert(
            documents=[text_representation],
            embeddings=vector,
            metadatas=[{"source": "previous_search", "query": query}],
            ids=[doc_id]
        )
        logger.info("💾 Saved new finding to local memory.")