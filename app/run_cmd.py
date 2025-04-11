import paramiko
from .config import settings
#from paramiko import RSAKey
import os



def do_set_static_route(droplet_ip):
    ssh_user = settings.DO_USERNAME  
    ssh_key_path =  os.path.expanduser(settings.SSH_KEY_PATH)
     
    #PASSWORD = settings.PASSWORD 
    #ssh_key = RSAKey(filename=ssh_key_path, password=PASSWORD)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    
    # ssh.connect(droplet_ip, username=ssh_user, pkey=ssh_key)

    ssh.connect(droplet_ip, username=ssh_user, key_filename=ssh_key_path)

    # Execute a command
    stdin, stdout, stderr = ssh.exec_command("ip route add 10.1.9.0/24 via 192.168.100.2")
    print(stdout.read().decode())

    # Close the connection
    ssh.close()

 

