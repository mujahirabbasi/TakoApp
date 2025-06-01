from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

# Create tables
from app.database import engine
Base.metadata.create_all(bind=engine) 