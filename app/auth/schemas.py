from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
class ShowUser(BaseModel):
    username: str
    email: str

class UserLogin(BaseModel):
    username: str
    email: str
    password: str

    

