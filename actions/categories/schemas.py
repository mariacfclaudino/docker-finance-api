from pydantic import BaseModel, ConfigDict

# Request model
class CategoryCreate(BaseModel):
    name: str
    type: str   

# Response model
class ShowCategory(BaseModel):
    id: int
    name: str
    type: str

    model_config = ConfigDict(from_attributes=True)