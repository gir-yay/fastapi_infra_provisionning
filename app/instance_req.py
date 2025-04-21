import digitalocean
import time
from .config import settings


manager = digitalocean.Manager(token=settings.DO_API_KEY)



def create_droplet(droplet_name):

    
    droplet = digitalocean.Droplet(token=manager.token,
                               name= droplet_name,
                               region= settings.REGION, 
                               image= settings.IMAGE, 
                               size_slug= settings.SIZE_SLUG, 
                               vpc_uuid=settings.VPC_UUID ,
                               ssh_keys=[settings.SSH_KEY_ID], 
                               monitoring=True, 
                               backups=False,
                               tags=["Internal"]
                               )
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



def add_dns_record(name, ip_address):
    domain_obj = digitalocean.Domain(token=manager.token, name=settings.DOMAIN_NAME)
    
    record = digitalocean.Record(
        token=manager.token,
        domain=domain_obj,
        type='A',
        name=name,  
        data=ip_address,
        ttl=3600
    )
    record.create()
    print(f"DNS A record created: {name}.{settings.DOMAIN_NAME} -> {ip_address}")


def delete_dns_record(name):
    domain_obj = digitalocean.Domain(token=manager.token, name=settings.DOMAIN_NAME)
    records = domain_obj.get_records()

    for record in records:
        if record.name == name and record.type == "A":
            record.destroy()
            print(f"Deleted A record: {name}.{settings.DOMAIN_NAME}")
            return True
    print(f"No matching A record found for: {name}.{settings.DOMAIN_NAME}")
    return False


