from fastapi import  Response, status, HTTPException, Depends, APIRouter
from typing import  List
from .. import models, schemas , utils, oauth2
from ..database import  get_db
from sqlalchemy.orm import Session

from .. import instance_req as instReq
from .. import vm_req as vmReq
from .. import run_cmd as runcmd
import time
import subprocess, os
from ..config import settings
from .. import k8s 




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
    name = instance.instance_name + "-" + current_user.username
    domain_name= f"{name}.{settings.DOMAIN_NAME}"
    instance.instance_name = name
    lb_ip = settings.LB_IP
    instReq.add_dns_record(name, lb_ip)
    k8s.deploy_odoo(name)

    
    new_instance = models.Instances(owner_id= current_user.id, domain_name= domain_name , **instance.dict())
    db.add(new_instance)
    db.commit()
    db.refresh(new_instance)
    return new_instance


@router.delete("/{id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_instance(id: int , db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    instance_query = db.query(models.Instances).filter(models.Instances.id == id)
    instance = instance_query.first()
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    
    if instance.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    # Delete the instance
    k8s.delete_odoo(instance.instance_name)
    instReq.delete_dns_record(instance.instance_name)
    instance_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    

