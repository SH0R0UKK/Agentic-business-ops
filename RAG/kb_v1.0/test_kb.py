# =========================
# agentic_rag.py – Agentic Retrieval & Grading
# =========================

import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser

# 1. Load Environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables.")

# 2. Setup Embeddings (Same as before)
embeddings = GoogleGenerativeAIEmbeddings(
    model="text-embedding-004",
    google_api_key=api_key
)

# 3. Load Vector DB
print("... Loading Knowledge Base ...")
kb = Chroma(
    collection_name="kb_v1_0",
    embedding_function=embeddings,
    persist_directory="./chroma/kb_v1_0"
)

# 4. Setup the LLM (The "Brain")
# using gemini-1.5-flash because it is fast and cheap for grading tasks
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=api_key,
    temperature=0
)

# =========================
# AGENTIC STEP 1: RETRIEVAL
# =========================
query = "What are the key principles of Disciplined Entrepreneurship?"
print(f"\n🔎 Query: {query}")

# We retrieve more chunks (k=5) because we expect to throw some away
raw_results = kb.similarity_search(query, k=5)

# =========================
# AGENTIC STEP 2: THE GRADER
# =========================
print(f"\n... Grading {len(raw_results)} chunks for relevance ...")

# Prompt for the Grader Agent
grader_prompt = PromptTemplate(
    template="""You are a strict grader assessing the relevance of a retrieved document to a user question. 
    
    User Question: {question}
    
    Retrieved Document: 
    {context}
    
    CRITERIA:
    1. If the document is a Bibliography, Reference list, or Citation dump -> Grade: NO
    2. If the document discusses a DIFFERENT topic (e.g., Lean Startup instead of Disciplined Entrepreneurship) -> Grade: NO
    3. If the document contains relevant information to answer the question -> Grade: YES
    
    Give a binary score 'YES' or 'NO' only.
    """,
    input_variables=["question", "context"]
)

grader_chain = grader_prompt | llm | StrOutputParser()

valid_docs = []

for i, doc in enumerate(raw_results, 1):
    # The agent "reads" the doc
    grade = grader_chain.invoke({"question": query, "context": doc.page_content})
    cleaned_grade = grade.strip().upper()
    
    print(f"   - Chunk {i}: [Grade: {cleaned_grade}] - Source: {doc.metadata.get('source', 'Unknown')}")
    
    if "YES" in cleaned_grade:
        valid_docs.append(doc)

print(f"\n✅ {len(valid_docs)} valid chunks retained out of {len(raw_results)}.")

# =========================
# AGENTIC STEP 3: GENERATION
# =========================
if not valid_docs:
    print("\n❌ No relevant documents found. I cannot answer based on the knowledge base.")
else:
    print("\n... Generating Final Answer ...\n")
    
    # Combine valid chunk text
    context_text = "\n\n".join([d.page_content for d in valid_docs])
    
    # Prompt for Final Answer
    answer_prompt = PromptTemplate(
        template="""You are an expert assistant for a startup founder. Use the following context to answer the question. 
        If the answer is not in the context, say "I don't have enough information in my Knowledge Base."
        
        Context:
        {context}
        
        Question: 
        {question}
        
        Answer:
        """,
        input_variables=["context", "question"]
    )
    
    rag_chain = answer_prompt | llm | StrOutputParser()
    
    response = rag_chain.invoke({"context": context_text, "question": query})
    print(response)