# =========================
# kb1.py – Build KB_v1.0
# =========================

import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --------- Loaders ---------
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader
)

# --------- Text Splitter ---------
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --------- Gemini Embeddings ---------
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --------- Vector Store ---------
from langchain_community.vectorstores import Chroma


# =========================
# 1. Text Cleaning
# =========================
def clean_text(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


# =========================
# ... (imports remain the same)

# =========================
# 2. Load Documents
# =========================
print("Loading documents...")
docs = []

# Load MD
md_docs = UnstructuredMarkdownLoader(
    r"C:\Users\Amena\Downloads\MLOPs\Project\Agentic-business-ops\RAG\kb_v1.0\Disciplined Entrepreneurship Notes.md"
).load()
print(f"-> Loaded MD: {len(md_docs)} document(s)")
docs += md_docs

# Load HTML
html_docs = UnstructuredHTMLLoader(
    r"C:\Users\Amena\Downloads\MLOPs\Project\Agentic-business-ops\RAG\kb_v1.0\The Lean Startup _ Notes.html"
).load()
print(f"-> Loaded HTML: {len(html_docs)} document(s)")
docs += html_docs

# Load PDF (Using PyMuPDF - It is better/faster than PyPDF)
# If you don't have it: pip install langchain-community pymupdf
try:
    from langchain_community.document_loaders import PyMuPDFLoader
    pdf_loader = PyMuPDFLoader(r"C:\Users\Amena\Downloads\MLOPs\Project\Agentic-business-ops\RAG\kb_v1.0\Early_Startups.pdf")
except ImportError:
    # Fallback to PyPDF if PyMuPDF isn't installed
    pdf_loader = PyPDFLoader(r"C:\Users\Amena\Downloads\MLOPs\Project\Agentic-business-ops\RAG\kb_v1.0\Early_Startups.pdf")

pdf_docs = pdf_loader.load()
print(f"-> Loaded PDF: {len(pdf_docs)} pages")
docs += pdf_docs

# =========================
# 3. Clean & AUDIT Documents
# =========================
cleaned_docs = []
dropped_pages = 0

for doc in docs:
    original_len = len(doc.page_content)
    cleaned_text = clean_text(doc.page_content)
    doc.page_content = cleaned_text
    
    # Metadata updates
    doc.metadata["kb_version"] = "kb_v1.0"
    doc.metadata["ingested_at"] = datetime.utcnow().isoformat()
    
    # LOWER THE THRESHOLD: Changed from 200 to 50 to save diagrams/lists
    if len(cleaned_text) > 50: 
        cleaned_docs.append(doc)
    else:
        dropped_pages += 1
        # UNCOMMENT below to see exactly what is being deleted
        # print(f"WARNING: Dropped page from {doc.metadata.get('source')} (Length: {len(cleaned_text)})")

print(f"⚠️  Dropped {dropped_pages} pages due to low content length.")
docs = cleaned_docs


# =========================
# 4. Chunking
# =========================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

chunks = splitter.split_documents(docs)


# =========================
# 5. Gemini Embeddings
# =========================
embeddings = GoogleGenerativeAIEmbeddings(
    model="text-embedding-004",  # Gemini embedding model
    google_api_key=os.getenv("GEMINI_API_KEY")
)


# =========================
# 6. Build & Persist Chroma KB
# =========================
kb = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="kb_v1_0",
    persist_directory="./chroma/kb_v1_0"
)

kb.persist()


# =========================
# 7. Success Confirmation
# =========================
print("=" * 50)
print("✅ KB_v1.0 BUILT SUCCESSFULLY")
print(f"📄 Documents loaded   : {len(docs)}")
print(f"🧩 Chunks created     : {len(chunks)}")
print(f"📦 Chroma collection  : kb_v1_0")
print(f"💾 Persisted at       : ./chroma/kb_v1_0")
