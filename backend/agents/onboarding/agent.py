"""
Onboarding Agent - Business Context Extraction
Migrated from Gemini to Perplexity Sonar for consistency with backend
"""

import os
import json
import re
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

# Use Sonar Pro for document understanding (better for text-heavy analysis)
llm = ChatOpenAI(
    model="sonar",
    temperature=0.0,
    base_url="https://api.perplexity.ai",
    api_key=os.getenv("PERPLEXITY_API_KEY") or os.getenv("PPLX_API_KEY"),
    timeout=180,
    max_retries=3,
)


ONBOARDING_PROMPT = """
You are an expert business analyst extracting structured information from documents.

Your task:
Analyze the provided business materials and extract key information into a structured format.

EXTRACTION RULES:
- Extract ONLY factual information present in the documents
- Do NOT invent or assume information
- Use empty strings "" or empty lists [] if information is missing
- Be concise and factual
- Focus on business-relevant details

OUTPUT FORMAT (JSON):
{
  "business_name": "Official company/business name",
  "business_type": "Industry/sector (e.g., FinTech, E-commerce, SaaS)",
  "location": "City, Country or 'Egypt' if in Egypt",
  "stage": "Business stage (e.g., Idea, MVP, Seed, Series A)",
  "founded": "Year founded (if mentioned)",
  "goals": ["List of explicit business goals or objectives"],
  "key_constraints": ["Budget limits, regulatory issues, resource gaps"],
  "target_audience": "Primary customer segment description",
  "competitors": ["List of mentioned competitors"],
  "unique_value": "What makes this business different/unique",
  "sector": "Specific sector/niche",
  "team_size": "Number of employees/team members (if mentioned)"
}

IMPORTANT:
- Output ONLY valid JSON
- No markdown code blocks
- No explanations before or after JSON
- Accuracy over completeness
"""


def clean_json_output(raw_text: str) -> str:
    """Remove markdown and extract JSON from LLM response."""
    # Remove markdown code blocks
    cleaned = re.sub(r'```json\s*', '', raw_text, flags=re.MULTILINE)
    cleaned = re.sub(r'```\s*', '', cleaned, flags=re.MULTILINE)
    
    # Try to extract JSON object
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned, re.DOTALL)
    if json_match:
        return json_match.group(0).strip()
    
    return cleaned.strip()


def extract_business_context(processed_files: list[dict]) -> dict:
    """
    Extract business context from processed files using Sonar.
    
    Args:
        processed_files: List of dicts from ingestion.py with 'text', 'filename', 'type'
    
    Returns:
        dict: Extracted business context
    """
    # Build context from all files
    context_parts = []
    
    for file_data in processed_files:
        filename = file_data.get('filename', 'unknown')
        text = file_data.get('text', '')
        file_type = file_data.get('type', 'unknown')
        
        if text.strip():
            context_parts.append(f"=== FILE: {filename} ({file_type}) ===\n{text}\n")
    
    if not context_parts:
        raise ValueError("No text content found in any files")
    
    combined_context = "\n\n".join(context_parts)
    
    # Truncate if too long (Sonar has limits)
    max_chars = 50000
    if len(combined_context) > max_chars:
        print(f"⚠️ Context too long ({len(combined_context)} chars), truncating to {max_chars}")
        combined_context = combined_context[:max_chars] + "\n\n[... content truncated ...]"
    
    print(f"\n📋 Extracting context from {len(processed_files)} files ({len(combined_context)} chars)...")
    
    # Call Sonar
    messages = [
        SystemMessage(content=ONBOARDING_PROMPT),
        HumanMessage(content=combined_context)
    ]
    
    response = llm.invoke(messages)
    
    # Parse response
    cleaned = clean_json_output(response.content)
    
    try:
        business_context = json.loads(cleaned)
        print("✅ Business context extracted successfully")
        return business_context
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        print(f"Raw response: {response.content[:500]}...")
        raise


def run_onboarding(file_paths: list[str], org_id: str = "default") -> dict:
    """
    Main onboarding entry point.
    
    Args:
        file_paths: List of file paths to process
        org_id: Organization identifier
    
    Returns:
        dict with:
            - user_context: Extracted business information
            - processed_files: List of processed file data
            - org_id: Organization ID
    """
    from backend.agents.onboarding.ingestion import batch_process_files
    
    print(f"\n{'='*70}")
    print(f"🚀 ONBOARDING: Processing {len(file_paths)} files for org '{org_id}'")
    print(f"{'='*70}\n")
    
    # Step 1: Process files (extract text, images, etc.)
    processed_files = batch_process_files(file_paths)
    
    if not processed_files:
        raise ValueError("No files were successfully processed")
    
    print(f"\n✅ Processed {len(processed_files)} files")
    
    # Step 2: Extract business context using LLM
    business_context = extract_business_context(processed_files)
    
    # Step 3: Add metadata
    business_context['org_id'] = org_id
    business_context['available_documents'] = [f['filename'] for f in processed_files]
    
    # Step 4: Store in backend data structure
    result = {
        'user_context': business_context,
        'processed_files': processed_files,
        'org_id': org_id,
        'status': 'success'
    }
    
    print(f"\n{'='*70}")
    print(f"✅ ONBOARDING COMPLETE")
    print(f"{'='*70}")
    print(f"Business: {business_context.get('business_name', 'N/A')}")
    print(f"Type: {business_context.get('business_type', 'N/A')}")
    print(f"Location: {business_context.get('location', 'N/A')}")
    print(f"Goals: {len(business_context.get('goals', []))}")
    print(f"Documents: {len(processed_files)}")
    print(f"{'='*70}\n")
    
    return result


# Optional: Save to ChromaDB for RAG (using existing backend system)
def store_documents_in_rag(processed_files: list[dict], org_id: str):
    """
    Store processed documents in the backend RAG system.
    Uses the existing multilingual-e5-small embeddings.
    """
    from backend.agents.researcher.tools_offline import get_collection
    from sentence_transformers import SentenceTransformer
    
    collection = get_collection("onboarding_docs")
    model = SentenceTransformer('intfloat/multilingual-e5-small')
    
    ids = []
    documents = []
    metadatas = []
    
    for idx, file_data in enumerate(processed_files):
        text = file_data.get('text', '').strip()
        if not text:
            continue
        
        # Chunk if too long
        max_chunk_size = 1000
        if len(text) > max_chunk_size:
            # Simple chunking
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size-200)]
        else:
            chunks = [text]
        
        for chunk_idx, chunk in enumerate(chunks):
            doc_id = f"{org_id}_{file_data['filename']}_{idx}_{chunk_idx}"
            ids.append(doc_id)
            documents.append(chunk)
            metadatas.append({
                'org_id': org_id,
                'source': file_data['filename'],
                'type': file_data['type'],
                'chunk_index': chunk_idx
            })
    
    if ids:
        # Generate embeddings
        embeddings = model.encode(documents, show_progress_bar=True)
        
        # Store in ChromaDB
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings.tolist()
        )
        
        print(f"✅ Stored {len(ids)} chunks in RAG for org '{org_id}'")
