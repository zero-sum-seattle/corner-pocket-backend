from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from .base import Base

class User(Base):
    """A player in the pool hall.
    
    Represents someone who can challenge others to matches, track their
    wins/losses, and generally hustle around the virtual felt. Each user
    has a unique email and handle for identification.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)  # For login and contact
    handle = Column(String, unique=True, nullable=False)  # Public display name/username
    created_at = Column(DateTime, default=datetime.utcnow)  # When they joined the hall