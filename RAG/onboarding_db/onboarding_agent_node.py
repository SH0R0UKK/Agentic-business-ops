import os
import time
from pathlib import Path
import chromadb
from chromadb.api.types import EmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai

# -----------------------------
# 1. Gemini Embedding Function
# -----------------------------
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="models/text-embedding-004"):
        # Configure API once
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = model_name

    def __call__(self, texts):
        """
        Chroma expects: List[str] -> List[List[float]]
        """
        # Remove empty strings to prevent API errors
        texts = [t for t in texts if t.strip()]
        if not texts:
            return []

        embeddings = []
        # Loop is necessary as embed_content is single-input in some SDK versions,
        # but robust for lists in newer ones. keeping it safe.
        for text in texts:
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="RETRIEVAL_DOCUMENT",
                    title="Onboarding Context" # Optional: improves quality for some models
                )
                embeddings.append(result["embedding"])
                time.sleep(0.2) # Rate limit safety for free tier
            except Exception as e:
                print(f"Embedding failed for chunk: {e}")
                # Return zero vector or handle error - here we skip to avoid crash
                # In prod, you might want to retry or fail hard.
                embeddings.append([0.0] * 768) 
        
        return embeddings

# -----------------------------
# 2. Chroma Node (Onboarding Library)
# -----------------------------
def add_to_rag_library(
    org_id: str,
    documents: list[dict],
    collection_name: str = "onboarding_docs"
):
    """
    Ingests extracted text into the persistent RAG node.
    """
    # 1. Setup Persistence Path
    rag_path = Path("RAG").resolve()
    rag_path.mkdir(exist_ok=True)

    # 2. Initialize Persistent Client (The Fix)
    # strict_extensions=False allows for broader compatibility
    client = chromadb.PersistentClient(path=str(rag_path))

    embedding_fn = GeminiEmbeddingFunction()

    # 3. Get/Create Collection
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"} # Explicit distance metric
    )

    # 4. Splitting Strategy
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # Slightly larger for business context
        chunk_overlap=200,    # Good context overlap
        separators=["\n\n", "\n", ".", " ", ""]
    )

    ids, texts, metas = [], [], []

    for doc in documents:
        # Handle cases where content might be empty
        raw_content = doc.get("content", "")
        if not raw_content:
            continue

        chunks = splitter.split_text(raw_content)
        
        for i, chunk in enumerate(chunks):
            # Deterministic ID: org + filename + chunk_index
            chunk_id = f"{org_id}_{doc['filename']}_{i}"
            
            ids.append(chunk_id)
            texts.append(chunk)
            metas.append({
                "org_id": org_id,
                "source": doc["filename"],
                "node": "onboarding_library",
                "timestamp": str(time.time())
            })

    # 5. Batch Add (Upsert is safer than Add if running multiple times)
    if ids:
        collection.upsert(
            documents=texts,
            metadatas=metas,
            ids=ids
        )
        print(f"✅ Successfully indexed {len(ids)} chunks for {org_id}")
    else:
        print("⚠️ No content to index.")

    # Note: client.persist() is removed as it is deprecated in ChromaDB v0.4+
    # PersistentClient auto-saves.