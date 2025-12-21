import chromadb
import logging
import os
from sentence_transformers import SentenceTransformer
from .models import ResearchResult, OfflineEvidencePack, Claim, Contradiction
from . import llm_client

logger = logging.getLogger(__name__)

# Configuration
CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/chroma")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "benchmark_corpus")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")


class LocalLibrarian:
    def __init__(self, persist_path: str = None):
        """
        persist_path: Where the vector DB files are stored.
        """
        self.persist_path = persist_path or CHROMA_PATH
        
        # Ensure directory exists
        os.makedirs(self.persist_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.persist_path)
        
        # Try to get the benchmark corpus, fallback to agent_memory
        try:
            self.collection = self.client.get_collection(name=COLLECTION_NAME)
            logger.info(f"📚 Loaded collection: {COLLECTION_NAME}")
        except Exception:
            self.collection = self.client.get_or_create_collection(name="agent_memory")
            logger.info("📚 Using fallback collection: agent_memory")
        
        # Load embedding model (multilingual for Arabic + English)
        logger.info(f"📚 Loading embedding model: {EMBEDDING_MODEL}")
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)

    def search(self, query: str, threshold: float = 1.2, n_results: int = 5) -> ResearchResult | None:
        """
        Searches local DB. 
        Threshold: Lower = stricter match. 1.2 is a balanced starting point.
        """
        try:
            # Use e5 format for queries
            query_text = f"query: {query}"
            query_vec = self.encoder.encode([query_text], normalize_embeddings=True).tolist()
            
            results = self.collection.query(
                query_embeddings=query_vec,
                n_results=n_results
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
                    summary=doc_content[:500], 
                    key_statistics=["Retrieved from internal memory"],
                    citations=[metadata.get("url", metadata.get("source", "Internal Memory"))],
                    confidence_score=10,
                    source_type="local"
                )
            
            return None

        except Exception as e:
            logger.warning(f"⚠️ Local search error: {e}")
            return None

    def search_chunks(self, query: str, n_results: int = 10) -> list[dict]:
        """
        Retrieve top-k chunks with full metadata for LLM processing.
        Returns list of dicts with: chunk_id, text, source_title, url, doc_type, language, scope
        """
        try:
            query_text = f"query: {query}"
            query_vec = self.encoder.encode([query_text], normalize_embeddings=True).tolist()
            
            results = self.collection.query(
                query_embeddings=query_vec,
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results['documents'] or not results['documents'][0]:
                return []
            
            chunks = []
            for i, (doc, metadata, dist) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                chunks.append({
                    "chunk_id": results['ids'][0][i] if results.get('ids') else f"chunk_{i}",
                    "text": doc,
                    "source_title": metadata.get("title", "Unknown"),
                    "url": metadata.get("url", ""),
                    "doc_type": metadata.get("doc_type", "unknown"),
                    "language": metadata.get("language", "en"),
                    "scope": metadata.get("scope", "global"),
                    "distance": dist
                })
            
            logger.info(f"📚 Retrieved {len(chunks)} chunks for query")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Chunk search error: {e}")
            return []

    def save_memory(self, result: ResearchResult, query: str):
        """
        Saves a ResearchResult into the vector DB for future use.
        """
        text_representation = (
            f"Query: {query}\n"
            f"Summary: {result.summary}\n"
            f"Stats: {', '.join(result.key_statistics)}"
        )
        
        # Use e5 format for documents
        doc_text = f"passage: {text_representation}"
        vector = self.encoder.encode([doc_text], normalize_embeddings=True).tolist()
        
        # Unique ID based on query hash to avoid duplicates
        doc_id = f"mem_{hash(query)}"
        
        self.collection.upsert(
            documents=[text_representation],
            embeddings=vector,
            metadatas=[{"source": "previous_search", "query": query, "doc_type": "memory"}],
            ids=[doc_id]
        )
        logger.info("💾 Saved new finding to local memory.")


async def offline_research_with_llm(
    question: str, 
    startup_context: dict = None,
    n_chunks: int = 10
) -> OfflineEvidencePack:
    """
    High-level function that combines RAG retrieval with LLM reasoning.
    
    1) Retrieve relevant chunks from Chroma.
    2) Build context_chunks with text + metadata.
    3) Call llm_client.summarize_offline_context().
    4) Return a structured OfflineEvidencePack.
    
    Args:
        question: User's research question
        startup_context: Optional dict with startup profile info
        n_chunks: Number of chunks to retrieve
    
    Returns:
        OfflineEvidencePack with claims, contradictions, missing_info
    """
    librarian = LocalLibrarian()
    
    # Step 1: Retrieve chunks
    context_chunks = librarian.search_chunks(question, n_results=n_chunks)
    
    if not context_chunks:
        logger.warning("No chunks found for query")
        return OfflineEvidencePack(
            question=question,
            summary="No relevant information found in knowledge base.",
            claims=[],
            contradictions=[],
            missing_info=["No data available for this query in the knowledge base."],
            status="no_results"
        )
    
    # Step 2: Call LLM for summarization
    llm_result = await llm_client.summarize_offline_context(question, context_chunks)
    
    if not llm_result:
        logger.error("LLM summarization failed")
        return OfflineEvidencePack(
            question=question,
            summary="LLM processing failed. Raw chunks retrieved but not summarized.",
            claims=[],
            contradictions=[],
            missing_info=["LLM processing error"],
            status="error"
        )
    
    # Step 3: Parse LLM result into Pydantic model
    claims = []
    for c in llm_result.get("claims", []):
        claims.append(Claim(
            value=c.get("value", ""),
            source_chunk_id=str(c.get("source_chunk_id", "unknown")),
            url=c.get("url", ""),
            doc_type=c.get("doc_type", "unknown")
        ))
    
    contradictions = []
    for ct in llm_result.get("contradictions", []):
        contradictions.append(Contradiction(
            claim_a=ct.get("claim_a", ""),
            claim_b=ct.get("claim_b", ""),
            source_a=ct.get("source_a", ""),
            source_b=ct.get("source_b", "")
        ))
    
    return OfflineEvidencePack(
        question=question,
        summary=llm_result.get("summary", ""),
        claims=claims,
        contradictions=contradictions,
        missing_info=llm_result.get("missing_info", []),
        status="success"
    )