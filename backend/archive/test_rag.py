"""
Test RAG System - Query the ingested benchmark corpus
"""

import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

DATA_PATH = Path(r"C:\Users\hanae\OneDrive - Nile University\Desktop\MLops project\Agentic-business-ops\backend\data")
CHROMA_PATH = DATA_PATH / "chroma"
COLLECTION_NAME = "benchmark_corpus"
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"


def query_rag(query: str, n_results: int = 5):
    """Query the RAG system"""
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print('='*70)
    
    # Load model and collection
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_collection(COLLECTION_NAME)
    
    # Embed query (prefix with "query: " for e5 model)
    query_embedding = embedder.encode(f"query: {query}", normalize_embeddings=True)
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )
    
    # Display results
    if results['documents'] and results['documents'][0]:
        print(f"\nFound {len(results['documents'][0])} results:\n")
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            print(f"[{i+1}] Score: {1 - distance:.3f}")
            print(f"    Title: {metadata.get('title', 'N/A')}")
            print(f"    URL: {metadata.get('url', 'N/A')}")
            print(f"    Language: {metadata.get('language', 'N/A')}")
            print(f"    Type: {metadata.get('doc_type', 'N/A')}")
            print(f"    Content: {doc[:200]}...")
            print()
    else:
        print("No results found.")


if __name__ == "__main__":
    # Test queries
    test_queries = [
        "How to start a business in Egypt?",
        "What are the 24 steps of Disciplined Entrepreneurship?",
        "Explain the Lean Startup methodology",
        "How to validate product-market fit?",
        "كيف أحصل على تمويل لشركتي الناشئة في مصر؟",
        "What is the Build-Measure-Learn cycle?"
    ]
    
    print("="*70)
    print("RAG SYSTEM TEST")
    print("="*70)
    print(f"Data path: {DATA_PATH}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Model: {EMBEDDING_MODEL}")
    
    for query in test_queries:
        query_rag(query, n_results=3)
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
