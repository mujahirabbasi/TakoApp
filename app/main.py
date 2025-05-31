from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import secrets
from typing import Optional
from pydantic import BaseModel
import uvicorn
from sqlalchemy.orm import Session
from agent.kb_agent import run_custom_agent, initialize_ollama, initialize_embeddings, create_retriever_tool, create_web_search_tool
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA
from app.database import get_db, engine
from app.models.user import User, Base
from app.routers import auth
import os

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()

class Question(BaseModel):
    question: str

# Initialize KB Agent components
try:
    print("[DEBUG] Initializing Ollama...")
    initialize_ollama()
    print("[DEBUG] Ollama initialized.")
    print("[DEBUG] Initializing embeddings...")
    vectorstore = initialize_embeddings()
    print(f"[DEBUG] Vectorstore: {vectorstore}")
    print("[DEBUG] Setting up retriever...")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    print(f"[DEBUG] Retriever: {retriever}")
    print("[DEBUG] Loading LLM...")
    llm = ChatOllama(model="llama2", temperature=0)
    print(f"[DEBUG] LLM: {llm}")
    print("[DEBUG] Setting up retrieval chain...")
    retrieval_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    print(f"[DEBUG] Retrieval chain: {retrieval_chain}")
    retriever_tool = create_retriever_tool(retrieval_chain)
    print(f"[DEBUG] Retriever tool: {retriever_tool}")
    web_search_tool = create_web_search_tool()
    print(f"[DEBUG] Web search tool: {web_search_tool}")
    tools = [retriever_tool, web_search_tool]
    print("[DEBUG] Knowledge Base Agent initialized successfully.")
except Exception as e:
    print(f"[ERROR] Error initializing KB Agent: {str(e)}")
    tools = None
    llm = None
    retriever = None

# Include auth router
app.include_router(auth.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request, username: str):
    return templates.TemplateResponse("welcome.html", {"request": request, "username": username})

@app.post("/ask")
async def ask_question_post(question: Question):
    """POST endpoint for the question-answering functionality."""
    if not tools or not llm or not retriever:
        return JSONResponse(
            status_code=500,
            content={"error": "Knowledge Base Agent is not properly initialized"}
        )
    
    try:
        response = run_custom_agent(question.question, tools, llm, retriever)
        
        # Ensure answer and sources are always separated
        if isinstance(response, dict):
            answer = response.get('answer', '')
            sources = response.get('sources', [])
        else:
            answer = response
            sources = []
        
        return JSONResponse(content={
            "answer": answer,
            "sources": sources
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing question: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 