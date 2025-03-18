from fastapi import Depends, APIRouter, HTTPException, status, Response
from sqlalchemy.orm import Session
from .. import schemas, models, utils, oauth2
from ..database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags=["Authentication"],
)

@router.post("/login" , response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = db.query(models.Users).filter(models.Users.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    access_token = oauth2.create_jwt_token(data={ "user_id": user.id })
    return { "access_token": access_token, "token_type": "bearer" }