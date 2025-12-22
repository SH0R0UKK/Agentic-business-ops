"""
File Ingestion Utilities for Onboarding
Processes PDFs, images (with OCR), and text files into structured format
Combines PIL Image objects with text extraction for multimodal LLM processing
"""

import os
import mimetypes
from pathlib import Path
from PIL import Image
from pypdf import PdfReader
import pytesseract
import base64
from io import BytesIO

# Tesseract Configuration (optional - OCR will be skipped if not installed)
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string for LLM vision processing."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def process_file_input(file_path: str) -> tuple[list[dict], list[dict]]:
    """
    Process a single file and return structured data for both LLM and RAG.
    
    Returns:
        tuple: (agent_inputs, rag_documents)
            agent_inputs: List of dicts with 'type' and 'content' for LLM
                         - For images: content is PIL Image object
                         - For text: content is string
            rag_documents: List of dicts with 'filename' and 'content' for vector DB
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    mime_type, _ = mimetypes.guess_type(path)
    extension = path.suffix.lower()
    
    agent_inputs = []
    rag_documents = []
    
    print(f"🔄 Processing: {path.name} ({extension})")

    # ====================================================
    # CASE 1: IMAGES (With Optional OCR)
    # ====================================================
    if extension in ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif']:
        try:
            # Load image for LLM vision
            img = Image.open(path)
            agent_inputs.append({"type": "image", "content": img})
            print("   📸 Image loaded for multimodal LLM")
            
            # Try OCR if Tesseract available (for RAG searchability)
            if os.path.exists(TESSERACT_PATH):
                try:
                    ocr_text = pytesseract.image_to_string(img)
                    if ocr_text.strip():
                        print(f"   🔤 OCR extracted: {len(ocr_text)} chars")
                        
                        # Add OCR as text hint for LLM
                        agent_inputs.append({
                            "type": "text", 
                            "content": f"OCR Text from {path.name}:\n{ocr_text}"
                        })
                        
                        # Save to RAG for semantic search
                        rag_documents.append({
                            "filename": path.name,
                            "content": f"[OCR Content from Image]\n{ocr_text}"
                        })
                    else:
                        print("   ⚠️ OCR found no text in image")
                except Exception as e:
                    print(f"   ⚠️ OCR failed (non-fatal): {e}")
            else:
                print("   ⚠️ Tesseract not found, skipping OCR (image still processed by vision)")
                
        except Exception as e:
            print(f"   ❌ Image processing failed: {e}")
            raise
    
    # ====================================================
    # CASE 2: PDFs
    # ====================================================
    elif extension == '.pdf':
        try:
            reader = PdfReader(path)
            extracted_texts = []
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_texts.append(page_text)
            
            full_text = "\n\n".join(extracted_texts)
            
            # Add to LLM inputs
            agent_inputs.append({
                "type": "text", 
                "content": f"Content from PDF '{path.name}':\n{full_text}"
            })
            
            # Add to RAG
            rag_documents.append({
                "filename": path.name,
                "content": full_text
            })
            
            print(f"   📄 PDF extracted: {len(reader.pages)} pages, {len(full_text)} chars")
            
        except Exception as e:
            print(f"   ❌ PDF processing failed: {e}")
            raise
    
    # ====================================================
    # CASE 3: TEXT FILES
    # ====================================================
    elif extension in ['.txt', '.md', '.csv', '.json']:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            agent_inputs.append({
                "type": "text", 
                "content": f"Content from {path.name}:\n{content}"
            })
            
            rag_documents.append({
                "filename": path.name,
                "content": content
            })
            
            print(f"   📝 Text file loaded: {len(content)} chars")
            
        except Exception as e:
            print(f"   ❌ Text file processing failed: {e}")
            raise
    
    else:
        print(f"   ⚠️ Unsupported file type: {extension}")
        agent_inputs.append({
            "type": "text",
            "content": f"[Unsupported file type: {extension} - {path.name}]"
        })
    
    return agent_inputs, rag_documents


def batch_process_files(file_paths: list[str]) -> tuple[list[dict], list[dict]]:
    """
    Process multiple files and return combined inputs for LLM and RAG.
    
    Args:
        file_paths: List of file paths to process
    
    Returns:
        tuple: (all_agent_inputs, all_rag_documents)
    """
    all_agent_inputs = []
    all_rag_documents = []
    
    print(f"\n📂 Batch processing {len(file_paths)} files...")
    
    for file_path in file_paths:
        try:
            agent_inputs, rag_docs = process_file_input(file_path)
            all_agent_inputs.extend(agent_inputs)
            all_rag_documents.extend(rag_docs)
        except Exception as e:
            print(f"❌ Failed to process {file_path}: {e}")
            # Continue with other files
            continue
    
    print(f"✅ Batch processing complete: {len(all_agent_inputs)} inputs, {len(all_rag_documents)} documents")
    
    return all_agent_inputs, all_rag_documents
