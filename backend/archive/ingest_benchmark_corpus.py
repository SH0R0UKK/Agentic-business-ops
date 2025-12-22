"""
Data Ingestion Pipeline for Benchmark Corpus
Downloads, parses, chunks, embeds, and stores documents for RAG.
"""

import json
import sqlite3
import tempfile
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
import requests
from bs4 import BeautifulSoup
import PyPDF2
import chromadb
from sentence_transformers import SentenceTransformer

# === CONFIGURATION ===
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "db" / "advisor.db"
SOURCES_PATH = DATA_DIR / "benchmark_sources.json"
CHROMA_PATH = DATA_DIR / "chroma"
COLLECTION_NAME = "benchmark_corpus"
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
CHUNK_SIZE = 500  # tokens approx
CHUNK_OVERLAP = 50

# === DATABASE SETUP ===
def init_database():
    """Create SQLite tables if they don't exist"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            doc_type TEXT,
            scope TEXT,
            topic TEXT,
            language TEXT,
            corpus_type TEXT DEFAULT 'benchmark',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            page_or_slide TEXT,
            section_title TEXT,
            text TEXT NOT NULL,
            language TEXT,
            corpus_type TEXT DEFAULT 'benchmark',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)
    
    conn.commit()
    conn.close()

# === DOWNLOAD ===
def download_content(url: str, retries: int = 3) -> Optional[tuple]:
    """Download content from URL. Returns (content_bytes, content_type) or None"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower()
            return response.content, content_type
        except Exception as e:
            if attempt == retries - 1:
                return None
    return None

# === PARSING ===
def parse_pdf(content: bytes) -> str:
    """Extract text from PDF bytes"""
    text_parts = []
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(content)
            f.flush()
            
            with open(f.name, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            Path(f.name).unlink()
    except Exception:
        pass
    
    return "\n\n".join(text_parts)

def parse_html(content: bytes) -> str:
    """Extract text from HTML bytes"""
    try:
        soup = BeautifulSoup(content, "html.parser")
        
        # Remove scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        # Get main content
        main = soup.find("main") or soup.find("article") or soup.find("body")
        if main:
            text = main.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)
        
        # Normalize whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        
        return text.strip()
    except Exception:
        return ""

def parse_content(content: bytes, content_type: str, url: str) -> str:
    """Parse content based on type"""
    if "pdf" in content_type or url.endswith(".pdf"):
        return parse_pdf(content)
    else:
        return parse_html(content)

# === CHUNKING ===
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """Split text into chunks. Simple word-based chunking."""
    if not text.strip():
        return []
    
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
        if start >= len(words):
            break
    
    return chunks

# === EMBEDDING ===
def get_embedder():
    """Load embedding model"""
    return SentenceTransformer(EMBEDDING_MODEL)

def embed_chunks(chunks: list, embedder) -> list:
    """Generate embeddings for chunks using e5 format"""
    # For documents, prefix with "passage: "
    prefixed = [f"passage: {chunk}" for chunk in chunks]
    embeddings = embedder.encode(prefixed, normalize_embeddings=True)
    return embeddings.tolist()

# === STORAGE ===
def get_chroma_collection():
    """Get or create ChromaDB collection"""
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    # Delete existing collection to start fresh
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
    
    return client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def store_document(conn, source: dict, language: str) -> int:
    """Store document in SQLite, return document_id"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO documents (title, url, doc_type, scope, topic, language, corpus_type)
        VALUES (?, ?, ?, ?, ?, ?, 'benchmark')
    """, (
        source["title"],
        source["url"],
        source.get("doc_type"),
        source.get("scope"),
        source.get("topic"),
        language
    ))
    conn.commit()
    return cursor.lastrowid

def store_chunks(conn, doc_id: int, chunks: list, language: str) -> list:
    """Store chunks in SQLite, return chunk IDs"""
    cursor = conn.cursor()
    chunk_ids = []
    
    for idx, chunk_text in enumerate(chunks):
        cursor.execute("""
            INSERT INTO chunks (document_id, chunk_index, text, language, corpus_type)
            VALUES (?, ?, ?, ?, 'benchmark')
        """, (doc_id, idx, chunk_text, language))
        chunk_ids.append(cursor.lastrowid)
    
    conn.commit()
    return chunk_ids

def store_in_chroma(collection, chunk_ids: list, chunks: list, embeddings: list, metadata: dict):
    """Store chunks with embeddings in ChromaDB"""
    ids = [str(cid) for cid in chunk_ids]
    metadatas = [metadata.copy() for _ in chunks]
    
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

# === MAIN INGESTION ===
def ingest():
    """Main ingestion pipeline"""
    print("=" * 60)
    print("RAG Ingestion Pipeline")
    print("=" * 60)
    
    # Load sources
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        sources = json.load(f)
    
    print(f"\nLoaded {len(sources)} sources from {SOURCES_PATH}")
    
    # Validate sources
    required_fields = ["url", "title", "doc_type", "scope", "topic"]
    valid_sources = []
    skipped = []
    
    for src in sources:
        if all(src.get(f) for f in required_fields):
            valid_sources.append(src)
        else:
            skipped.append({"url": src.get("url", "unknown"), "title": src.get("title", "unknown"), "status": "skipped", "notes": "missing required fields"})
    
    print(f"Valid sources: {len(valid_sources)}")
    print(f"Skipped (invalid): {len(skipped)}")
    
    # Initialize
    init_database()
    embedder = get_embedder()
    collection = get_chroma_collection()
    conn = sqlite3.connect(DB_PATH)
    
    # Process each source
    report = []
    total_chunks = 0
    
    for i, source in enumerate(valid_sources):
        url = source["url"]
        title = source["title"]
        language = source.get("language_hint", "en")
        
        print(f"\n[{i+1}/{len(valid_sources)}] {title[:50]}...")
        
        entry = {
            "url": url,
            "title": title,
            "status": None,
            "num_chunks": 0,
            "language": language,
            "notes": ""
        }
        
        # Download
        result = download_content(url)
        if result is None:
            entry["status"] = "download_failed"
            entry["notes"] = "failed to download"
            report.append(entry)
            print(f"  ❌ Download failed")
            continue
        
        content, content_type = result
        
        # Parse
        text = parse_content(content, content_type, url)
        if not text or len(text) < 50:
            entry["status"] = "parse_failed"
            entry["notes"] = "no content extracted"
            report.append(entry)
            print(f"  ❌ Parse failed")
            continue
        
        # Chunk
        chunks = chunk_text(text)
        if not chunks:
            entry["status"] = "parse_failed"
            entry["notes"] = "no chunks created"
            report.append(entry)
            print(f"  ❌ No chunks")
            continue
        
        # Embed
        try:
            embeddings = embed_chunks(chunks, embedder)
        except Exception as e:
            entry["status"] = "parse_failed"
            entry["notes"] = f"embedding error: {str(e)[:50]}"
            report.append(entry)
            print(f"  ❌ Embedding failed")
            continue
        
        # Store in SQLite
        doc_id = store_document(conn, source, language)
        chunk_ids = store_chunks(conn, doc_id, chunks, language)
        
        # Store in ChromaDB
        metadata = {
            "url": url,
            "title": title,
            "doc_type": source.get("doc_type", ""),
            "scope": source.get("scope", ""),
            "topic": source.get("topic", ""),
            "language": language,
            "corpus_type": "benchmark"
        }
        store_in_chroma(collection, chunk_ids, chunks, embeddings, metadata)
        
        entry["status"] = "embedded"
        entry["num_chunks"] = len(chunks)
        report.append(entry)
        total_chunks += len(chunks)
        
        print(f"  ✓ {len(chunks)} chunks embedded")
    
    conn.close()
    
    # Add skipped sources to report
    report.extend(skipped)
    
    # Generate final report
    final_report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_sources": len(sources),
            "successfully_embedded": sum(1 for r in report if r["status"] == "embedded"),
            "total_chunks": total_chunks,
            "download_failed": sum(1 for r in report if r["status"] == "download_failed"),
            "parse_failed": sum(1 for r in report if r["status"] == "parse_failed"),
            "skipped": sum(1 for r in report if r["status"] == "skipped")
        },
        "sources": report
    }
    
    # Print summary
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"Total sources: {final_report['summary']['total_sources']}")
    print(f"Successfully embedded: {final_report['summary']['successfully_embedded']}")
    print(f"Total chunks: {final_report['summary']['total_chunks']}")
    print(f"Download failed: {final_report['summary']['download_failed']}")
    print(f"Parse failed: {final_report['summary']['parse_failed']}")
    print(f"Skipped: {final_report['summary']['skipped']}")
    
    # Save report
    report_path = DATA_DIR / "ingestion_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved to: {report_path}")
    
    return final_report


if __name__ == "__main__":
    ingest()
