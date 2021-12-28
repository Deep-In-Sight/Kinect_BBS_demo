import sys
import paramiko
from scp import SCPClient
#from datetime import datetime
#from datetime import timedelta

from bbsQt.constants import DIR_KEY_SERVER, HOST, S_ACCOUNT, S_PASSWORD, SCP_PORT

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

ssh = createSSHClient(HOST, SCP_PORT, S_ACCOUNT, S_PASSWORD)
scp = SCPClient(ssh.get_transport())

fn = sys.argv[1]
scp.put(fn, DIR_KEY_SERVER, recursive=True)
print("put", fn, "to", DIR_KEY_SERVER)
