import socket
import os

#Website with TCP instruction: https://www.thepythoncode.com/article/send-receive-files-using-sockets-python

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step


def getHostInfo():
    try:
        host_name = socket.gethostname()
        self.ip = socket.gethostbyname(host_name)
        return host_name, self.ip, self.port
    except socket.error:
        print("Unable to get Hostname and/or IP Address")