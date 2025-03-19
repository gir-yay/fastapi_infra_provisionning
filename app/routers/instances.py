from fastapi import  Response, status, HTTPException, Depends, APIRouter
from typing import  List
from .. import models, schemas , utils, oauth2
from ..database import  get_db
from sqlalchemy.orm import Session

from .. import instance_req as instReq


router = APIRouter(
    prefix="/instances",
    tags=["Instances"],
)




@router.get("/", response_model=List[schemas.InstanceResponse])
def get_instace( db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    inst = db.query(models.Instances).filter(models.Instances.owner_id == current_user.id ).all()
    if not inst:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="No instances running")

    return inst


@router.post("/",  status_code=status.HTTP_201_CREATED , response_model=schemas.InstanceResponse)
def create_instance(instance : schemas.InstanceCreate , db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    instance_id , instance_ip = instReq.create_droplet(instance.instance_name)
    new_instance = models.Instances(owner_id= current_user.id,  instance_id=instance_id, instance_ip=instance_ip, **instance.dict())
    db.add(new_instance)
    db.commit()
    db.refresh(new_instance)
    return new_instance


@router.delete("/{id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_instance(id: int , db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    instance = db.query(models.Instances).filter(models.Instances.id == id).first()
    
    if instance:
        if instance.owner_id != current_user.id:
            raise HTTPException(status_code= status.HTTP_403_FORBIDDEN , detail="Instance does not exist!")
        db.delete(instance)
        #post.delete(synchronize_session=False)
        instReq.delete_droplet(instance.instance_id)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="Instance not found")


