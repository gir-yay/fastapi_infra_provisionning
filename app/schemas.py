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

    

class Token(BaseModel):
    access_token: str 
    token_type: str



class TokenData(BaseModel):
    id: Optional[int] = None
    


class InstanceCreate(BaseModel):
    instance_name: str


class InstanceResponse(BaseModel):
    id : int
    instance_name : str
    instance_ip : str
    domain_name: Optional[str] = None

    class Config:
        orm_mode = True
        #from_attributes = True