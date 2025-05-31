from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.auth.utils import verify_password, get_password_hash
from app.database import get_db
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, success: str = None):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "success": success
        }
    )

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Email not registered"}
        )
    
    if not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Incorrect password"}
        )
    
    return RedirectResponse(url=f"/welcome?username={user.username}", status_code=303)

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user exists
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered"}
        )
    
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Passwords do not match"}
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )
    
    try:
        db.add(new_user)
        db.commit()
        return RedirectResponse(
            url="/login?success=Registration successful! Please login with your credentials.",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "An error occurred during registration"}
        )

@router.get("/logout")
async def logout():
    return RedirectResponse(
        url="/login?success=You have been successfully logged out.",
        status_code=303
    ) 