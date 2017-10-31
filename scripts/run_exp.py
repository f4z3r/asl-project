#!/usr/bin python3

import os
import time
import paramiko

class Client:
    def __init__(self, hostname):
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.connect(hostname, username="bjakob")

    def run(self, command):
        self.ssh.exec_command(command)

    def kill(self, process):
        stdin, stdout, stderr = self.ssh.exec_command("ps -A")
        for line in stdout.read().splitlines():
            if process in line:
                pid = int(line.spit(None, 1)[0])
                self.run("kill -SIGINT %d" % pid)


def scp_put(localfile, remote_host, remote_file):
    """
    Copies the file in the argument to the remote host.
    """
    os.system("scp -rp -o StrictHostKeyChecking=no %s %s:%s" % \
              (localfile, remote_host, remote_file))

def scp_get(remote_host, remote_file, local_dir):
    """
    Copies files from remote host to local machine.
    """
    os.system("scp -rp -o StrictHostKeyChecking=no %s:%s %s" % \
              (remote_host, remote_file, local_dir))

if __name__ == "__main__":
    # Set experiment variables
    MID_THREADS = 3
    MID_SHARDED = "false"
    MID_LOCAL_IP = "10.0.0.1"
    SERVER_IP = "48.32.45.102"
    TEST_TIME = 20


    # Scp required files to the VMs
    scp_put("/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/" +\
            "gitlab/asl-fall17-project/middleware/dist/middleware-bjakob.jar",
            "bjakob@bjakobforaslvms4.westeurope.cloudapp.azure.com",
            "middleware-bjakob.jar")

    # Create SSH clients
    memtier = Client("bjakobforaslvms1.westeurope.cloudapp.azure.com")
    middleware = Client("bjakobforaslvms4.westeurope.cloudapp.azure.com")
    server = Client("bjakobforaslvms6.westeurope.cloudapp.azure.com")

    server.run("sudo service memcached stop")
    server.run("memcached -p 11211")

    time.sleep(1)       # Give server time to start

    middleware.run("jar xvf middleware-bjakob.jar")
    time.sleep(1)
    middleware.run("java -cp . asl_project.RunMW -l %s -p 8000 -t %d -s %s -m%s:11211" %\
                   (MID_LOCAL_IP, MID_THREADS, MID_SHARDED, SERVER_IP))

    time.sleep(1)
    memtier.run(("memtier_benchmark-master/memtier_benchmark --server=%s " +\
                 "--port=8000 --expiry-range=9999-10000 --key-maximum=1000 " +\
                 "--ratio=1:99 --test-time=%s --protocol=memcache_text > memtier.log") %\
                (MID_LOCAL_IP, TEST_TIME))

    time.sleep(TEST_TIME)

    middleware.kill("RunMW")
    server.kill("memcached")
    time.sleep(1)
    server.run("sudo service memcached stop")

    scp_get("bjakob@bjakobforaslvms4.westeurope.cloudapp.azure.com", "analysis.log", "~/Desktop")
    scp_get("bjakob@bjakobforaslvms4.westeurope.cloudapp.azure.com", "system.log", "~/Desktop")
    scp_get("bjakob@bjakobforaslvms1.westeurope.cloudapp.azure.com", "memtier.log", "~/Desktop")
