from fastapi import  Response, status, HTTPException, Depends, APIRouter
from typing import  List
from .. import models, schemas , utils, oauth2
from ..database import  get_db
from sqlalchemy.orm import Session
from ..config import settings

import digitalocean
import time


manager = digitalocean.Manager(token=settings.DO_API_KEY)



router = APIRouter(
    prefix="/instances",
    tags=["Instances"],
)

def create_droplet(droplet_name):
    droplet = digitalocean.Droplet(token=manager.token,
                               name= droplet_name,
                               region='nyc1', # Amster
                               image='ubuntu-20-04-x64',
                               size_slug='s-1vcpu-1gb',  
                               ssh_keys=[45450783], 
                               backups=False)
    droplet.create()
    
    droplet_id = None
    public_ip = None

    while not droplet_id or not public_ip:
        droplets = manager.get_all_droplets()

        for d in droplets:
            if d.name == droplet_name:
                droplet_id = d.id  # Get droplet ID if not set

                # Check for public IPv4
                for network in d.networks['v4']:
                    if network['type'] == 'public':
                        public_ip = network['ip_address']
                        break

        if droplet_id and public_ip:
            break  # Exit loop once both are retrieved

        time.sleep(5)  # Wait before checking again

    print(f"Droplet '{droplet_name}' created with ID: {droplet_id}, Public IPv4: {public_ip}")

    return droplet_id, public_ip


def delete_droplet(droplet_id):
    droplet = digitalocean.Droplet(token=manager.token, id=droplet_id)
    droplet.destroy()
    print("Droplet destroyed.")





@router.get("/", response_model=List(schemas.InstanceResponse))
def get_user( db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.Instances).filter(models.Instances.owner_id == current_user.id ).all
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="Something went wrong")

    return user


@router.post("/",  status_code=status.HTTP_201_CREATED , response_model=schemas.InstanceResponse)
def create_instance(instance : schemas.InstanceCreate , db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    instance.instance_id , instance.instance_ip = create_droplet(instance.instance_name)
    new_instance = models.Instances(user_id= current_user.id, **instance.dict())
    db.add(new_instance)
    db.commit()
    db.refresh(new_instance)
    return new_instance


@router.delete("/{id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_instance(id: int , db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    instance = db.query(models.Instances).filter(models.Instances.id == id).first()
    
    if instance:
        if instance.user_id != current_user.id:
            raise HTTPException(status_code= status.HTTP_403_FORBIDDEN , detail="Instance does not exist!")
        db.delete(instance)
        #post.delete(synchronize_session=False)
        delete_droplet(instance.instance_id)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="Instance not found")


