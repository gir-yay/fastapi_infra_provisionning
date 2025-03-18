from fastapi import  Response, status, HTTPException, Depends, APIRouter
from typing import  List
from .. import models, schemas , utils, oauth2
from ..database import  get_db
from sqlalchemy.orm import Session



router = APIRouter(
    prefix="/instances",
    tags=["Instances"],
)


@router.get("/", response_model=List(schemas.InstanceResponse))
def get_user( db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.Instances).filter(models.Instances.owner_id == current_user.id ).all
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="Something went wrong")

    return user