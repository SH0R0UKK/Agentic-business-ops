"""
Onboarding Agent
Extracts business context from uploaded documents using Google Gemini
"""

import os
import json
import re
import time
from pathlib import Path
import google.generativeai as genai
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .ingestion import batch_process_files
from .prompts import ONBOARDING_EXTRACTION_PROMPT

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("Gemini_api_key")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

# Gemini model for document understanding
llm_onboarding = genai.GenerativeModel("gemini-2.5-flash-lite")

# Embedding model (same as RAG pipeline)
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
embedding_model = None  # Lazy load


def clean_json_output(raw_text: str) -> str:
    """
    Clean LLM output to extract valid JSON.
    Handles markdown code blocks, extra text, and whitespace.
    """
    # Remove markdown code blocks
    cleaned = re.sub(r'```json\s*', '', raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r'```\s*', '', cleaned, flags=re.IGNORECASE)
    
    # Try to find JSON object
    json_match = re.search(r'\{[\s\S]*\}', cleaned)
    if json_match:
        return json_match.group(0).strip()
    
    return cleaned.strip()


def extract_business_context(agent_inputs: list[dict], rag_documents: list[dict]) -> dict:
    """
    Extract business context from processed files using Gemini.
    
    Args:
        agent_inputs: List of inputs for LLM (images as PIL objects, text as strings)
        rag_documents: List of documents for RAG storage
    
    Returns:
        dict: Structured business context
    """
    print("\n🤖 ONBOARDING: Extracting business context with Gemini...")
    
    # Combine all text inputs
    combined_text = ""
    for inp in agent_inputs:
        if inp['type'] == 'text':
            combined_text += inp['content'] + "\n\n"
    
    if not combined_text.strip():
        combined_text = "No text content extracted from files."
    
    # Prepare Gemini prompt
    full_prompt = f"{ONBOARDING_EXTRACTION_PROMPT}\n\nDOCUMENT CONTENT:\n{combined_text}"
    
    try:
        # Call Gemini
        response = llm_onboarding.generate_content(full_prompt)
        raw_output = response.text
        
        # Clean and parse JSON
        cleaned = clean_json_output(raw_output)
        business_context = json.loads(cleaned)
        
        # Enforce available_documents from actual files
        business_context['available_documents'] = [doc['filename'] for doc in rag_documents]
        
        print(f"✅ Business context extracted: {business_context.get('business_name', 'N/A')}")
        
        return business_context
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"   Raw output: {raw_output[:500]}...")
        
        # Return minimal context
        return {
            "business_name": "Unknown",
            "business_type": "Unknown",
            "location": "Unknown",
            "stage": "Unknown",
            "goals": [],
            "constraints": [],
            "target_audience": "Unknown",
            "sector": "Unknown",
            "available_documents": [doc['filename'] for doc in rag_documents]
        }
    
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        raise


def store_in_chroma(org_id: str, rag_documents: list[dict]):
    """
    Store processed documents in ChromaDB with sentence-transformer embeddings.
    Uses the same embedding model as the RAG pipeline.
    """
    global embedding_model
    
    if not rag_documents:
        print("⚠️ No documents to store in ChromaDB")
        return
    
    print(f"\n📊 Storing {len(rag_documents)} documents in ChromaDB...")
    
    # Lazy load embedding model
    if embedding_model is None:
        print(f"   Loading embedding model: {EMBEDDING_MODEL}")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    
    # Setup ChromaDB path
    chroma_path = Path(__file__).parent.parent.parent.parent / "data" / "knowledge_base"
    chroma_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize client
    client = chromadb.PersistentClient(path=str(chroma_path))
    
    # Get or create collection with custom embedding function
    collection = client.get_or_create_collection(
        name="onboarding_docs",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    ids, texts, metas, embeddings = [], [], [], []
    
    for doc in rag_documents:
        content = doc.get("content", "")
        if not content:
            continue
        
        chunks = splitter.split_text(content)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{org_id}_{doc['filename']}_{i}"
            ids.append(chunk_id)
            texts.append(chunk)
            metas.append({
                "org_id": org_id,
                "source": doc["filename"],
                "node": "onboarding",
                "timestamp": str(time.time())
            })
            
            # Generate embedding
            embedding = embedding_model.encode(chunk).tolist()
            embeddings.append(embedding)
    
    # Store in ChromaDB
    if ids:
        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metas,
            embeddings=embeddings
        )
        print(f"✅ Stored {len(ids)} chunks in ChromaDB")


def run_onboarding(file_paths: list[str], org_id: str = "default") -> dict:
    """
    Main onboarding workflow: Process files and extract business context.
    
    Args:
        file_paths: List of file paths to process
        org_id: Organization identifier for RAG storage
    
    Returns:
        dict with keys:
            - user_context: Extracted business context
            - processed_files: List of processed file data
    """
    print(f"\n{'='*80}")
    print("🚀 ONBOARDING WORKFLOW STARTED")
    print(f"{'='*80}")
    print(f"Organization: {org_id}")
    print(f"Files to process: {len(file_paths)}")
    
    # Step 1: Process files
    agent_inputs, rag_documents = batch_process_files(file_paths)
    
    if not agent_inputs:
        print("❌ No valid inputs extracted from files")
        return {
            "user_context": {
                "business_name": "Unknown",
                "business_type": "Unknown",
                "location": "Unknown",
                "stage": "Unknown",
                "goals": [],
                "constraints": [],
                "target_audience": "Unknown",
                "sector": "Unknown",
                "available_documents": []
            },
            "processed_files": []
        }
    
    # Step 2: Extract business context
    business_context = extract_business_context(agent_inputs, rag_documents)
    
    # Step 3: Store in ChromaDB with embeddings
    try:
        store_in_chroma(org_id, rag_documents)
    except Exception as e:
        print(f"⚠️ ChromaDB storage failed (non-fatal): {e}")
    
    print(f"\n{'='*80}")
    print("✅ ONBOARDING WORKFLOW COMPLETED")
    print(f"{'='*80}")
    print(f"Business: {business_context.get('business_name', 'N/A')}")
    print(f"Type: {business_context.get('business_type', 'N/A')}")
    print(f"Stage: {business_context.get('stage', 'N/A')}")
    print(f"Documents processed: {len(rag_documents)}")
    
    return {
        "user_context": business_context,
        "processed_files": rag_documents
    }


# ==========================================
# TEST BLOCK
# ==========================================
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test with source folder files
    SOURCE_DIR = Path(__file__).parent.parent.parent.parent.parent / "source"
    
    test_files = []
    if SOURCE_DIR.exists():
        test_files = [str(f) for f in SOURCE_DIR.iterdir() if f.is_file()]
    
    if not test_files:
        print("⚠️ No files found in source directory")
        print(f"   Looking in: {SOURCE_DIR}")
        exit(1)
    
    print(f"Found {len(test_files)} files in source directory:")
    for f in test_files:
        print(f"  - {Path(f).name}")
    
    # Run onboarding
    result = run_onboarding(
        file_paths=test_files,
        org_id="test_org"
    )
    
    print("\n" + "="*80)
    print("EXTRACTION RESULTS")
    print("="*80)
    print(json.dumps(result['user_context'], indent=2))
