import paramiko
from .config import settings
#from paramiko import RSAKey
import os
import json




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
    
    nginx_config = f"""
    server {{
        listen 80;
        server_name {domain};

        location / {{
            proxy_pass http://{droplet_ip}:8069;
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


def delete_nginx_reverse_proxy_config(reverse_proxy_ip, droplet_name):

    ssh_user = settings.DO_USERNAME  
    ssh_key_path = os.path.expanduser(settings.SSH_KEY_PATH)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(reverse_proxy_ip, username=ssh_user, key_filename=ssh_key_path)

    try:
        commands = [
            f"sudo rm -f /etc/nginx/sites-available/{droplet_name}",
            f"sudo rm -f /etc/nginx/sites-enabled/{droplet_name}",
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


def setup_docker_remote(droplet_ip):

    ssh_user = settings.DO_USERNAME  
    ssh_key_path =  os.path.expanduser(settings.SSH_KEY_PATH)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(droplet_ip, username=ssh_user, key_filename=ssh_key_path)
   
    commands = [
        "apt-get install -y curl python3-pip",
        "curl -fsSL https://get.docker.com -o get-docker.sh && sh ./get-docker.sh"
    ]


    try:
      
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print("STDOUT:")
            print(stdout.read().decode())
            print("STDERR:")
            print(stderr.read().decode())

    except Exception as e:
        print(f"SSH connection failed: {e}")
    finally:
        ssh.close()




def create_prometheus_target_file(hostname, database_ip, droplet_name):

    target_file_path = f"/etc/prometheus/targets/{droplet_name}.json"
    data = [
        {
            "targets": [f"{database_ip}:9100"],
            "labels": {
                "job": "vsphere",
                "datacenter": "DC2",
                "instance": f"{droplet_name}",
            }
        }
    ]
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=settings.USERNAME, password=settings.PASSWORD)
        json_data = json.dumps(data, indent=2)
        command = f'echo \'{json_data}\' | sudo -S tee {target_file_path} > /dev/null'

        stdin, stdout, stderr = ssh.exec_command(command)
        error = stderr.read().decode()
        if error:
            print(f"Error creating file: {error}")
        else:
            print(f"File successfully created at {target_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        ssh.close()


def delete_prometheus_target_file(hostname, droplet_name):
    target_file_path = f"/etc/prometheus/targets/{droplet_name}.json"
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=settings.USERNAME, password=settings.PASSWORD)
        command = f'sudo -S rm {target_file_path}'

        stdin, stdout, stderr = ssh.exec_command(command)
        error = stderr.read().decode()
        if error:
            print(f"Error deleting file: {error}")
        else:
            print(f"File successfully deleted at {target_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        ssh.close()