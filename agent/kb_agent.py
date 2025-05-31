"""
Knowledge Base Agent - A tool for answering questions using document embeddings and web search.
"""

# Standard library imports
import os
import sys
import time
import json
import certifi

# Third-party imports
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chains import RetrievalQA
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, AgentOutputParser
from langchain.schema import AgentAction, AgentFinish, Document
from tabulate import tabulate

# Local imports
from agent.utils import (
    compute_and_store_embeddings,
    wait_for_ollama,
    check_and_pull_model
)

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
    print("Initializing Ollama models...")
    embedding = OllamaEmbeddings(model="llama2")
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../db")
    db_dir = os.path.abspath(db_dir)
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
    docs_dir = os.path.abspath(docs_dir)

    from agent.utils.compute_embeddings import split_markdown_sections
    from agent.utils.hash_utils import compute_document_hash, load_document_hash, save_document_hash

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

    if os.path.exists(os.path.join(db_dir, "chroma.sqlite3")) and current_hash == saved_hash:
        print("Loading existing vectorstore from database...")
        return Chroma(
            persist_directory=db_dir,
            embedding_function=embedding
        )
    else:
        print("No existing database found or documents changed. Computing embeddings...")
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

def validate_document_sources(docs, question):
    """Filter out irrelevant documents based on question context."""
    q = question.lower()
    valid_sources = {
        'employment': ['labor_rules.md', 'hr_manual.md'],
        'product': ['product_usage_manual.md'],
        'hr': ['hr_manual.md']
    }
    
    # Determine question type
    if any(word in q for word in ['labor', 'employment', 'work', 'employee', 'law', 'legal']):
        valid_files = valid_sources['employment']
        print(f"🔍 Question type: Employment/Labor - Valid files: {valid_files}")
    elif any(word in q for word in ['product', 'board', 'hardware', 'setup']):
        valid_files = valid_sources['product']
        print(f"🔍 Question type: Product - Valid files: {valid_files}")
    elif any(word in q for word in ['hr', 'policy', 'workplace']):
        valid_files = valid_sources['hr']
        print(f"🔍 Question type: HR - Valid files: {valid_files}")
    else:
        valid_files = [f for files in valid_sources.values() for f in files]
        print(f"🔍 Question type: General - Valid files: {valid_files}")
    
    # Filter documents and sort by relevance
    filtered_docs = [doc for doc in docs if doc.metadata.get('source') in valid_files]
    print(f"📚 Documents after source filtering: {len(filtered_docs)}")
    
    # Additional relevance check based on section headers
    if filtered_docs:
        # First, check for exact header matches
        exact_matches = []
        partial_matches = []
        question_words = set(q.split())
        
        for doc in filtered_docs:
            header = doc.metadata.get('header', '').lower()
            # Check for exact header match
            if header == q:
                exact_matches.append(doc)
                print(f"✅ Exact header match found: {header}")
            # Check for partial matches
            elif any(word in header for word in question_words):
                partial_matches.append(doc)
                print(f"✅ Partial header match found: {header}")
        
        # Combine matches with exact matches first
        filtered_docs = exact_matches + partial_matches + [doc for doc in filtered_docs if doc not in exact_matches and doc not in partial_matches]
        print(f"📚 Documents after header matching: {len(filtered_docs)}")
    
    return filtered_docs

def route_question(question, retriever):
    """Decide which tool to use based on document relevance and keywords."""
    q = question.lower()
    relevant_docs = retriever.invoke(question)
    # Filter out irrelevant documents
    relevant_docs = validate_document_sources(relevant_docs, question)
    has_relevant_docs = len(relevant_docs) > 0
    has_doc_keywords = any(keyword in q for keyword in ALL_DOCUMENT_KEYWORDS)
    needs_current_info = any(word in q for word in ["current", "latest", "today", "real-time", "now"])

    if has_relevant_docs:
        if has_doc_keywords:
            print("\n📚 Found relevant documents and matching keywords")
        else:
            print("\n📚 Found relevant documents (no keywords matched)")
        return "Document Retriever", relevant_docs
    
    if needs_current_info:
        print("\n🌐 Question requires current information")
        return "Web Search", []
    
    print("\n🤖 Using LLM for general knowledge")
    return "Final Answer", []

def run_custom_agent(question, tools, llm, retriever):
    """Run the appropriate tool based on the question routing."""
    tool_choice, relevant_docs = route_question(question, retriever)
    print(f"\n🔧 Using tool: {tool_choice}")

    if tool_choice == "Document Retriever":
        try:
            # Get relevant documents first
            relevant_docs = retriever.invoke(question)
            print(f"\n📚 Retrieved {len(relevant_docs)} documents initially")
            
            # Filter out irrelevant documents
            relevant_docs = validate_document_sources(relevant_docs, question)
            print(f"📚 After filtering: {len(relevant_docs)} documents")
            
            # Sort documents by relevance to question
            relevant_docs.sort(key=lambda x: len(set(question.lower().split()) & 
                                                set(x.metadata.get('header', '').lower().split())), 
                             reverse=True)
            
            print("\n📄 Documents used:")
            for i, doc in enumerate(relevant_docs, 1):
                print(f"{i}. Source: {doc.metadata.get('source')}")
                print(f"   Section: {doc.metadata.get('header')}")
                print(f"   Content preview: {doc.page_content[:100]}...")
            
            # Get answer from retrieval chain
            answer = tools[0].func(question)
            
            # Format answer with sources
            formatted_response = format_answer_with_sources(answer, relevant_docs)
            return formatted_response
        except Exception as e:
            print("Document retrieval failed, falling back to LLM...")
            return llm.invoke(question)
    
    if tool_choice == "Final Answer":
        try:
            return llm.invoke(question)
        except Exception as e:
            print("LLM generation failed, falling back to web...")
            return tools[1].func(question)

    if tool_choice == "Web Search":
        return tools[1].func(question)

# ===== Main Execution =====

def main():
    """Main execution function."""
    # Initialize Ollama
    initialize_ollama()

    # Initialize vector store and retriever
    vectorstore = initialize_embeddings()
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 10  # Increased from 3 to 10 to get more potential matches
        }
    )

    # Initialize LLM and retrieval chain
    llm = ChatOllama(model="llama2", temperature=0)
    retrieval_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    # Create tools
    retriever_tool = create_retriever_tool(retrieval_chain)
    web_search_tool = create_web_search_tool()
    tools = [retriever_tool, web_search_tool]

    # Create agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=5,
        early_stopping_method="generate",
        handle_parsing_errors=True
    )

    # Main interaction loop
    print("\nKnowledge Base Agent is ready! You can start asking questions.")
    print("\nCommands:")
    print("  - Type 'exit' to quit")

    while True:
        question = input("\nAsk a question or enter a command: ")
        
        if question.lower() == "exit":
            break
        else:
            try:
                response = run_custom_agent(question, tools, llm, retriever)
                print("\n📘 Answer:", response)
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try rephrasing your question in natural language.")

def format_answer_with_sources(answer, docs):
    """Format the answer to show which parts came from which sources."""
    # If answer is a dictionary, extract the result
    if isinstance(answer, dict) and 'result' in answer:
        answer_text = answer['result']
    else:
        answer_text = answer

    # Get source information as a list
    sources = [
        f"{doc.metadata.get('source')}: {doc.metadata.get('header')}"
        for doc in docs
    ]

    return {
        "answer": answer_text,
        "sources": sources
    }

if __name__ == "__main__":
    os.environ['LANGCHAIN_VERBOSE'] = 'true'
    main()
