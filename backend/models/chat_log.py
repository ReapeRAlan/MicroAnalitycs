from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base  # Changed from .base to ..base

class ChatLog(Base):
    __tablename__ = 'chat_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    mensaje = Column(String)
    respuesta = Column(String)
    
    user = relationship("User", back_populates="chat_logs")