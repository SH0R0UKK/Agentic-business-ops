"""
Setup file for Agentic Business Ops backend.
Install in editable mode: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="agentic-business-ops",
    version="1.0.0",
    description="AI-powered business consultancy platform for Egyptian startups",
    author="Your Team",
    packages=find_packages(include=["backend", "backend.*"]),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "langgraph>=0.0.20",
        "langchain-openai>=0.0.5",
        "langchain-core>=0.1.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "pypdf>=3.0.0",
        "python-dotenv>=1.0.0",
        "langsmith>=0.0.60",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "httpx>=0.25.0",
        "pillow>=10.0.0",
        "pytesseract>=0.3.10",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
