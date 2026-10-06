from app.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)        
    type = Column(String)       
    balance = Column(Integer)    
    
    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transactions", back_populates="account")
    
    
    
    
    
    