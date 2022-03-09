
import os,sys
import paramiko
from scp import SCPClient
import credential
def uploadFile(filename):

    hostname = 'x.x.x.x' 
    myuser   = 'xxxxxxxxx'
    mySSHK   = 'xxxxxxxx'
    sshcon   = paramiko.SSHClient()  # will create the object
    sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # no known_hosts error
    sshcon.connect(hostname, username=myuser, key_filename=mySSHK) # no passwd needed
    scp = SCPClient(sshcon.get_transport())
    #stdin, stdout, stderr = sshcon.exec_command('ls')
    #print (stdout.readlines())
    print(filename[0])
    print(filename)
    if filename[0].isdigit():
        scp.put(".//uploads//" + filename, remote_path="/shared/home/biohaviour_cyclecloud/workload/scripts/uploads/")
        print("If")
    else:
        scp.put(filename, remote_path="/shared/home/biohaviour_cyclecloud/workload/scripts/uploads/")
        print("Else")
    scp.close()
    sshcon.close()
    
