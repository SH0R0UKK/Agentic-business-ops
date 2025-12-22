from dotenv import load_dotenv
load_dotenv()  # Load .env before anything else

import os
# Force project name for LangSmith
#os.environ["LANGCHAIN_TRACING_V2"] = "true"
#os.environ["LANGCHAIN_PROJECT"] = "agentic-business-ops"

import json
import re
from langsmith import traceable
from onboarding.prompt import ONBOARDING_WALLET_PROMPT
from onboarding.schema import UserContext
from llm.multimodal import call_multimodal_llm
from storage.wallet_writer import write_wallet
from RAG.onboarding_db.onboarding_agent_node import add_to_rag_library

def clean_json_output(raw_text: str) -> str:
    """Removes markdown backticks and whitespace to ensure valid JSON parsing."""
    cleaned = re.sub(r"^```json", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"^```", "", cleaned, flags=re.MULTILINE)
    return cleaned.strip()

#@traceable(run_type="chain", name="Onboarding Workflow")
def run_onboarding(
    org_id: str, 
    extracted_inputs: list, 
    extracted_documents: list,
    user_request: str = ""  # <--- NEW ARGUMENT
):
    """
    Ingests files to create a Wallet (Context) and RAG (Memory).
    Passes the 'user_request' through for the future Orchestrator.
    """

    # 1. Extraction (The LLM only sees the files, not the request)
    #    We do NOT send user_request here because the LLM's job is 
    #    purely objective fact extraction, not following user orders yet.
    raw = call_multimodal_llm(
        system_prompt=ONBOARDING_WALLET_PROMPT,
        inputs=extracted_inputs
    )
    
    # 2. Cleaning & Parsing
    cleaned_raw = clean_json_output(raw)
    try:
        user_context = json.loads(cleaned_raw)
    except json.JSONDecodeError:
        print(f"FAILED TO PARSE JSON: {raw}")
        raise

    # 3. Enforce Ground Truth
    real_filenames = [d["filename"] for d in extracted_documents]
    user_context["available_documents"] = real_filenames

    # 4. Validation & Storage (Saves the Wallet to disk)
    validated_wallet = UserContext(**user_context).model_dump()
    write_wallet(validated_wallet, org_id)

    # 5. RAG Ingestion
    add_to_rag_library(org_id=org_id, documents=extracted_documents)

    # 6. RETURN THE PACKET (Wallet + Request)
    #    This is what the Orchestrator will receive.
    return {
        "wallet": validated_wallet,
        "user_request": user_request
    }

# ==========================================
# TEST BLOCK
# ==========================================
if __name__ == "__main__":
    from onboarding.ingestion import process_file_input
    
    # 1. Batch Configuration
    FILES_TO_UPLOAD = [
        r"C:\Users\Amena\Downloads\Gemini_Generated_Image_xydn8kxydn8kxydn.png",
        r"C:\Users\Amena\Downloads\Document.pdf"
        # Add other files here...
    ]
    
    # 2. The User Request (Instruction for the future)
    #    We renamed this from USER_CONTEXT
    USER_REQUEST = """
    I want to create a marketing campaign for next month.
    Please use the SWOT analysis in the image to identify opportunities.
    """

    print(f"🚀 Starting Onboarding with Request: '{USER_REQUEST.strip().splitlines()[0]}...'")

    # 3. Accumulate Inputs
    all_agent_inputs = [] 
    all_rag_docs = []      

    for file_path in FILES_TO_UPLOAD:
        try:
            if not os.path.exists(file_path):
                print(f"⚠️ Skipping missing file: {file_path}")
                continue
            
            inputs, docs = process_file_input(file_path)
            all_agent_inputs.extend(inputs)
            all_rag_docs.extend(docs)
            
        except Exception as e:
            print(f"❌ Failed to process {file_path}: {e}")

    # 4. Run the Agent
    if not all_agent_inputs:
        print("❌ No valid inputs found. Exiting.")
        exit()

    try:
        unique_org_id = "urban_plant_life_v2"
        
        # We pass the Request here, but the Agent just holds onto it
        output_packet = run_onboarding(
            org_id=unique_org_id,
            extracted_inputs=all_agent_inputs,
            extracted_documents=all_rag_docs,
            user_request=USER_REQUEST
        )
        
        print("\n✅ ONBOARDING COMPLETE! Output Packet for Orchestrator:")
        print(json.dumps(output_packet, indent=2))
        
    except Exception as e:
        print(f"\n❌ Agent Failed: {e}")