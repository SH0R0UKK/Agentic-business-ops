import os
import google.generativeai as genai
from PIL import Image
from langsmith import traceable

# Use the efficient 1.5 Flash model (or swap to "gemini-1.5-pro" for higher reasoning)
MODEL_ID = "gemini-2.5-flash" 

#@traceable(run_type="llm", name="Gemini Extraction")
def call_multimodal_llm(system_prompt: str, inputs: list) -> str:
    """
    Adapts the internal agent input format to the Google Gemini API.
    
    Args:
        system_prompt: The instructions for the agent (Wallet extraction rules).
        inputs: List of dicts, e.g.:
            [
                {"type": "text", "content": "Here is the business doc..."},
                {"type": "image", "content": <PIL.Image object>}
            ]
            
    Returns:
        str: The raw JSON string extracted by the LLM.
    """
    
    # 1. Configure API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)

    # 2. Initialize Model with System Instruction
    model = genai.GenerativeModel(
        model_name=MODEL_ID,
        system_instruction=system_prompt,
        generation_config={
            "temperature": 0.0,         # Deterministic output
            "response_mime_type": "application/json" # Enforce JSON mode
        }
    )

    # 3. Convert Internal "Inputs" to Gemini "Parts"
    gemini_parts = []
    
    for item in inputs:
        if item["type"] == "text":
            gemini_parts.append(item["content"])
        elif item["type"] == "image":
            # Gemini Python SDK accepts PIL Images directly
            gemini_parts.append(item["content"])
        else:
            print(f"⚠️ Warning: Unknown input type {item.get('type')}, skipping.")

    # 4. Generate Content
    try:
        response = model.generate_content(gemini_parts)
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        # Return empty JSON string to prevent crash, or re-raise if critical
        return "{}"