from fastapi import  Response, status, HTTPException, Depends, APIRouter
from typing import  List
from .. import models, schemas , utils, oauth2
from ..database import  get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post("/",  status_code=status.HTTP_201_CREATED , response_model=schemas.UserResponse)
def create_user(user : schemas.UserCreate , db: Session = Depends(get_db)):

    user.password = utils.hash_password(user.password)

    new_user = models.Users(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="User not found")

    return user