from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id : int
    username : str
    email : EmailStr

    class Config:
        orm_mode  = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Better be names PostBase
class Instance(BaseModel):
    instance_name: str
    

    

class PostResponse(BaseModel):
    id : int
    title : str
    content : str
    published : bool
    owner : UserResponse
    #created_at : datetime

    class Config:
        orm_mode = True
        #from_attributes = True




class Token(BaseModel):
    access_token: str 
    token_type: str



class TokenData(BaseModel):
    id: Optional[int] = None
    


