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

 
def setup_nginx_reverse_proxy(reverse_proxy_ip, droplet_ip , domain, droplet_name):
    """
    Set up Nginx reverse proxy on a remote server via SSH.
    """
    nginx_config = f"""
server {{
    listen 80;
    server_name {domain};

    location / {{
        proxy_pass http://{droplet_ip};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
""" 
    ssh_user = settings.DO_USERNAME  
    ssh_key_path =  os.path.expanduser(settings.SSH_KEY_PATH)
     

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(reverse_proxy_ip, username=ssh_user, key_filename=ssh_key_path)

    try:
        sftp = client.open_sftp()
        with sftp.file(f'/etc/nginx/sites-available/{droplet_name}', 'w') as f:
            f.write(nginx_config)
        sftp.close()

        commands = [
            f"sudo rm -f /etc/nginx/sites-enabled/{droplet_name}",
            f"sudo ln -sf /etc/nginx/sites-available/{droplet_name} /etc/nginx/sites-enabled/",
            "sudo nginx -t",
            "sudo systemctl reload nginx"
        ]

        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            exit_code = stdout.channel.recv_exit_status()
            if exit_code != 0:
                err_output = stderr.read().decode()
                raise Exception(f"Command failed: {cmd}\n{err_output}")

    finally:
        client.close()


