"""
Knowledge Base Agent - A tool for answering questions using document embeddings and web search.
"""

# Standard library imports
import os
import certifi

# Third-party imports
from dotenv import load_dotenv
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain.agents import Tool
from langchain.chains import RetrievalQA
from langchain_community.tools import DuckDuckGoSearchRun
# Local imports
from agent.utils import (
    compute_and_store_embeddings,
    wait_for_ollama,
    check_and_pull_model
)
from agent.utils.compute_embeddings import split_markdown_sections
from agent.utils.hash_utils import compute_document_hash, load_document_hash, save_document_hash

# ===== Configuration =====

# Load environment variables
load_dotenv(override=True)

# Set proper SSL certificate path
os.environ['SSL_CERT_FILE'] = certifi.where()

# Document categories and keywords for routing
DOCUMENT_KEYWORDS = {
    "HR Manual": [
        "workplace policies", "working hours", "leaves", "holidays", 
        "code of conduct", "employee rights", "responsibilities",
        "vacation", "sick days", "employee", "hr", "policy"
    ],
    "Labor Rules": [
        "legal labor", "obligations", "safety regulations", 
        "employee protections", "statutory benefits", "employment law",
        "labor law", "overtime", "safety", "employment"
    ],
    "Product Usage Manual": [
        "technical specifications", "hardware setup", "board components",
        "usb", "hdmi", "interface", "boot process", "operating systems",
        "rock960", "board", "setup", "product", "specifications"
    ]
}

# Flatten keywords for searching
ALL_DOCUMENT_KEYWORDS = [keyword for keywords in DOCUMENT_KEYWORDS.values() for keyword in keywords]

# ===== Initialization =====

def initialize_ollama():
    """Initialize Ollama and ensure it's running."""
    if not wait_for_ollama():
        raise RuntimeError("""
        Ollama is not running! Please:
        1. Make sure Ollama is installed from https://ollama.ai/download
        2. Start Ollama from your Start menu
        3. Try running this script again
        """)
    check_and_pull_model()

def initialize_embeddings():
    """Initialize or load the vector store, only recompute if docs changed."""
    embedding = OllamaEmbeddings(model="llama2")
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
    db_dir = os.path.abspath(db_dir)
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
    docs_dir = os.path.abspath(docs_dir)

    # Compute current hash
    markdown_files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
    all_docs = []
    for doc_file in markdown_files:
        file_path = os.path.join(docs_dir, doc_file)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = split_markdown_sections(text, doc_file)
        all_docs.extend(chunks)
    current_hash = compute_document_hash(all_docs)
    saved_hash = load_document_hash()

    if current_hash == saved_hash:
        return Chroma(
            persist_directory=db_dir,
            embedding_function=embedding
        )
    else:
        vectorstore = compute_and_store_embeddings()
        save_document_hash(current_hash)
        return vectorstore

# ===== Tool Definitions =====

def create_retriever_tool(retrieval_chain):
    """Create the document retriever tool."""
    return Tool(
        name="Document Retriever",
        func=lambda q: retrieval_chain.invoke(q),
        description=f"""
Use this tool to answer questions specifically about the following topics:

1. **HR Manual** — {', '.join(DOCUMENT_KEYWORDS['HR Manual'])}
2. **Labor Rules** — {', '.join(DOCUMENT_KEYWORDS['Labor Rules'])}
3. **Product Usage Manual** — {', '.join(DOCUMENT_KEYWORDS['Product Usage Manual'])}

Use this tool *only* when the question contains relevant keywords from the above categories.
If the question doesn't relate to these documents, do not use this tool.
"""
    )

def create_web_search_tool():
    """Create the web search tool with rate limiting protection."""
    search = DuckDuckGoSearchRun()

    def safe_search(query):
        """Wrapper for web search with rate limiting protection."""
        time.sleep(2)  # Wait to reduce rate limit hits
        try:
            return search.run(query)
        except Exception as e:
            return f"Unable to search the web at this time. Please try again later. Error: {str(e)}"

    return Tool(
        name="Web Search",
        func=safe_search,
        description="""Search the web for questions not covered in the documentation.
        Use this for current information like laws, market rates, or recent changes.
        Input should be a plain question like 'What is the current minimum wage?'"""
    )

# ===== Question Routing =====

def route_question(question, retriever):
    """Decide which tool to use based on document relevance and keywords."""
    q = question.lower()
    relevant_docs = retriever.invoke(question)
    has_relevant_docs = len(relevant_docs) > 0
    has_doc_keywords = any(keyword in q for keyword in ALL_DOCUMENT_KEYWORDS)
    needs_current_info = any(word in q for word in ["current", "latest", "today", "real-time", "now"])

    if has_relevant_docs:
        if has_doc_keywords:
            return "Document Retriever", relevant_docs
        else:
            return "Document Retriever", relevant_docs
    if needs_current_info:
        return "Web Search", relevant_docs
    return "Final Answer", relevant_docs

def run_custom_agent(question, tools, llm, retriever):
    """Run the appropriate tool based on the question routing."""
    tool_choice, relevant_docs = route_question(question, retriever)

    if tool_choice == "Document Retriever":
        try:
            # Get relevant documents
            # relevant_docs = retriever.invoke(question)
            # Sort documents by relevance to question
            relevant_docs.sort(key=lambda x: len(set(question.lower().split()) & 
                                                set(x.metadata.get('header', '').lower().split())), 
                             reverse=True)
            # Get answer from retrieval chain
            answer = tools[0].func(question)
            # Format answer with sources
            return format_answer_with_sources(answer, relevant_docs)
        except Exception as e:
            return {
                "answer": llm.invoke(question),
                "sources": []
            }
    
    if tool_choice == "Final Answer":
        try:
            return {
                "answer": llm.invoke(question),
                "sources": []
            }
        except Exception as e:
            return {
                "answer": tools[1].func(question),
                "sources": ["Web Search"]
            }

    if tool_choice == "Web Search":
        return {
            "answer": tools[1].func(question),
            "sources": ["Web Search"]
        }

def format_answer_with_sources(answer, docs):
    """Format the answer to show which parts came from which sources (top-k matched chunks)."""
    # If answer is a dictionary, extract the result
    if isinstance(answer, dict) and 'result' in answer:
        answer_text = answer['result']
    else:
        answer_text = answer

    # Get source information as a list of dicts with only file and section (header)
    sources = []
    for doc in docs:
        source = doc.metadata.get('source', '')
        header = doc.metadata.get('header', '')
        # Remove markdown header prefix if present (e.g., '## ')
        if header.startswith('## '):
            header = header[3:].strip()
        sources.append({
            "source": source,
            "header": header
        })

    return {
        "answer": answer_text,
        "sources": sources
    }
