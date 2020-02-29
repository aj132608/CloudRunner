import os

username = "ubuntu"
from scp import SCPClient
from paramiko import SSHClient, AutoAddPolicy

ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect(hostname="52.53.226.167",
            username=username,
            key_filename=os.path.join(os.getcwd(), "test_proj2_key.pem"))

with SCPClient(ssh.get_transport()) as scp:
    scp.put(os.path.join(os.getcwd(), "configs"), "configs",
            recursive=True)