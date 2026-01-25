"""
Start the API server with proper error handling.
This script ensures all imports work correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🚀 Starting Agentic Business Ops API Server...")
print("⏳ Loading dependencies (this may take 10-30 seconds)...")

# Load environment first
from dotenv import load_dotenv
load_dotenv()

# Import uvicorn for serving
import uvicorn

if __name__ == "__main__":
    # Start the server
    uvicorn.run(
        "backend.api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development with auto-reload
        log_level="info"
    )
