from pydantic import BaseModel, ConfigDict

# Request model
class CreateAccount(BaseModel):
    name: str # ex: "Conta corrente", "Poupança"
    type: str # ex: "checking", "savings", "credit"
    balance: int

# Response model
class ShowAccount(BaseModel):
    id: int
    name: str
    type: str
    balance: int

    model_config = ConfigDict(from_attributes=True)