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
    dname = instance.instance_name + "-" + current_user.username
    domain_name= f"{dname}.{settings.DOMAIN_NAME}"
    instance.instance_name = name
    instance_id , instance_ip = instReq.create_droplet(name)
    lb_ip = settings.LB_IP
    reverse_proxy_ip = settings.REVERSE_PROXY_IP
    #database_ip = vmReq.deploy_vm(name)
    #runcmd.do_set_static_route(instance_ip)
    database_ip = "192.168.100.4"
    
    time.sleep(60)

    runcmd.setup_docker_remote(instance_ip)

    ssh_key_path =  os.path.expanduser(settings.SSH_KEY_PATH)

    env = os.environ.copy()  
    env["PATH"] += ":/home/vscode/.local/bin"
    
    subprocess.run([
        "ansible-playbook",
        "/usr/src/app/playbooks/odoo.yml",
        "-i", f"{instance_ip},",  
        "-u", "root",
        "--private-key", ssh_key_path,
        "-e", f"target_host={instance_ip} server_ip={database_ip}",
        "-e", "ansible_ssh_common_args='-o StrictHostKeyChecking=no'"
    ], env=env)
    
    
    
    instReq.add_dns_record(dname, lb_ip)
    runcmd.setup_nginx_reverse_proxy(reverse_proxy_ip, instance_ip, domain_name, name)

    new_instance = models.Instances(owner_id= current_user.id,  instance_id=instance_id, instance_ip=instance_ip, database_ip = database_ip, domain_name= domain_name , **instance.dict())
    db.add(new_instance)
    db.commit()
    db.refresh(new_instance)
    return new_instance


@router.delete("/{id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_instance(id: int , db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    instance = db.query(models.Instances).filter(models.Instances.id == id).first()
    reverse_proxy_ip = settings.REVERSE_PROXY_IP
    
    if instance:
        if instance.owner_id != current_user.id:
            raise HTTPException(status_code= status.HTTP_403_FORBIDDEN , detail="Instance does not exist!")
        db.delete(instance)
        runcmd.delete_nginx_reverse_proxy_config(reverse_proxy_ip , instance.instance_name)
        instReq.delete_dns_record(instance.instance_name)
        
        instReq.delete_droplet(instance.instance_id)
        
        #vmReq.delete_vm(instance.instance_name)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="Instance not found")


