import os
import mimetypes
from pathlib import Path
from PIL import Image
from pypdf import PdfReader
import pytesseract

# ---------------------------------------------------------
# CONFIGURATION: Point to your Tesseract EXE
# ---------------------------------------------------------
# If you haven't installed the .exe yet, OCR will simply be skipped,
# but the Agent will still see the image!
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def process_file_input(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    mime_type, _ = mimetypes.guess_type(path)
    extension = path.suffix.lower()
    
    agent_inputs = []
    rag_documents = []
    
    print(f"🔄 Processing: {path.name} ({extension})")

    # ====================================================
    # CASE 1: IMAGES (Resilient Logic)
    # ====================================================
    if extension in ['.png', '.jpg', '.jpeg', '.webp', '.bmp']:
        # STEP A: Always load the image for the Agent (CRITICAL)
        try:
            img = Image.open(path)
            agent_inputs.append({"type": "image", "content": img})
            print("   📸 Image loaded for Agent.")
        except Exception as e:
            print(f"   ❌ Critical: Could not open image file: {e}")
            return [], []

        # STEP B: Try OCR for RAG (OPTIONAL BONUS)
        try:
            print("   🔍 Attempting OCR...")
            if not os.path.exists(TESSERACT_PATH):
                print("   ⚠️ Tesseract not found. Skipping OCR (Text won't be searchable).")
            else:
                ocr_text = pytesseract.image_to_string(img)
                
                if ocr_text.strip():
                    print(f"   ✅ OCR extracted {len(ocr_text)} chars.")
                    
                    # Add OCR text as a hint for the Agent
                    agent_inputs.append({
                        "type": "text", 
                        "content": f"OCR Text Hint:\n{ocr_text}"
                    })

                    # Save to RAG
                    rag_documents.append({
                        "filename": path.name,
                        "content": f"[OCR Content from Image]\n{ocr_text}"
                    })
                else:
                    print("   ⚠️ OCR found no text.")

        except Exception as e:
            print(f"   ⚠️ OCR Failed (Non-fatal): {e}")

    # ====================================================
    # CASE 2: PDF
    # ====================================================
    elif extension == '.pdf':
        try:
            print("   📄 Extracting PDF text...")
            reader = PdfReader(path)
            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"
            
            agent_inputs.append({
                "type": "text", 
                "content": f"Here is the content of the PDF '{path.name}':\n{extracted_text}"
            })
            
            rag_documents.append({
                "filename": path.name,
                "content": extracted_text
            })
            print(f"   ✅ Extracted {len(extracted_text)} chars.")

        except Exception as e:
            print(f"   ❌ PDF Read Failed: {e}")

    # ====================================================
    # CASE 3: TEXT FILES
    # ====================================================
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            agent_inputs.append({"type": "text", "content": content})
            rag_documents.append({"filename": path.name, "content": content})
            
        except Exception as e:
            print(f"   ❌ Text Read Failed: {e}")

    return agent_inputs, rag_documents