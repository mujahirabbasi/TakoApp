from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from agent.kb_agent import run_custom_agent
from app.database import get_db, engine
from app.models.user import User, Base
from app.routers import auth, chat
from app.auth.auth import get_current_user
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
import secrets
from app.shared import tools, llm, retriever  # Import shared components

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

# Use this for templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))
# Create database tables
Base.metadata.create_all(bind=engine)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Question(BaseModel):
    question: str

# Include routers
app.include_router(auth.router)
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request, username: str):
    return templates.TemplateResponse("welcome.html", {"request": request, "username": username})

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("chat.html", {"request": request, "username": current_user.username})

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

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # Pass the error message as a query parameter
        return RedirectResponse(url=f"/login?error={exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

