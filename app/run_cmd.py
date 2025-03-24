import paramiko
from .config import settings
#from paramiko import RSAKey




def do_set_static_ip(droplet_ip):
    ssh_user = settings.DO_USERNAME  
    ssh_key_path = "./dokey2" 
    #PASSWORD = settings.PASSWORD 
    #ssh_key = RSAKey(filename=ssh_key_path, password=PASSWORD)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    
    # ssh.connect(droplet_ip, username=ssh_user, pkey=ssh_key)

    ssh.connect(droplet_ip, username=ssh_user, key_filename=ssh_key_path)

    # Execute a command
    stdin, stdout, stderr = ssh.exec_command("ip route add 10.1.9.0/24 via 192.168.100.3")
    print(stdout.read().decode())

    # Close the connection
    ssh.close()

 

def run_ssh_command_vm(VM_IP):
    USERNAME = settings.USERNAME
    PASSWORD = settings.PASSWORD
    COMMAND = "echo " +  PASSWORD + "| sudo -S ip route add 192.168.100.0/24 via 10.1.9.167" 
    #COMMAND = "sudo ip route add 192.168.100.0/24 via 10.1.9.167"
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(VM_IP, username=USERNAME, password=PASSWORD)

        stdin, stdout, stderr = client.exec_command(COMMAND)
        #stdin.write(PASSWORD + "\n")
        #stdin.flush()
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print("Output:\n", output)
        if error:
            print("Error:\n", error)

        client.close()
    except Exception as e:
        print(f"SSH Error: {e}")



