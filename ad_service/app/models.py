from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    price = Column(Integer, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())