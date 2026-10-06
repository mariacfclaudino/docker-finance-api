from pydantic import BaseModel, ConfigDict
from datetime import date

# Request model
class TransactionCreate(BaseModel):
    category_id: int
    amount: float
    description: str
    date: date
    
# Response model
class ShowTransaction(BaseModel):
    id: int
    account_id: int
    category_id: int
    amount: float
    description: str
    date: date
    type: str

    model_config = ConfigDict(from_attributes=True)