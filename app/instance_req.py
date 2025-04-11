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
                               tags=["Internal"])
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


