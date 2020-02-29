def scp_send(hostname, username, local_filepath,
        instance_filepath, key_filepath):
    """
    This function is used to send files over scp to
    a remote server.
    :param hostname: IP of the Host
    :param username: Username to login as
    :param local_filepath: Filepath of the folder to send
    :param instance_filepath: Target location in the remote instance
    :param key_filepath: Auth Token filepath
    :returns nothing:
    """
    from scp import SCPClient
    from paramiko import SSHClient, AutoAddPolicy

    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=hostname,
                    username=username,
                    key_filename=key_filepath)

        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_filepath, instance_filepath,
                    recursive=True)
        return True
    except:
        return False

def scp_get(hostname, username, local_filepath,
        instance_filepath, key_filepath):
    """
    This function is used to retrieve files over scp to
    a remote server.
    :param hostname: IP of the Host
    :param username: Username to login as
    :param local_filepath: Filepath of the folder to send
    :param instance_filepath: Target location in the remote instance
    :param key_filepath: Auth Token filepath
    :returns nothing:
    """
    from scp import SCPClient
    from paramiko import SSHClient, AutoAddPolicy

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostname=hostname,
                username=username,
                key_filename=key_filepath)

    with SCPClient(ssh.get_transport()) as scp:
        scp.get(instance_filepath, local_filepath,
                recursive=True)