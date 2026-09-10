from datetime import date 
from pydantic import BaseModel , ConfigDict 

class UserCreate(BaseModel):
    username : str
    passcode : str 
    dob : date 

class UserResponse(BaseModel):
    id : int 
    username : str
    dob : date 

    model_config = ConfigDict(from_attributes=True)

