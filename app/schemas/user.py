from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserInDB(UserBase):
    password: str  # Hashed password

class User(UserBase):
    pass 