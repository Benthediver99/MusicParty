import socket
import threading
import os

#Website with TCP instruction: https://www.thepythoncode.com/article/send-receive-files-using-sockets-python

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 # send 4096 bytes each time step
clients = {}
addresses = {}
HOST = ''
PORT = 33000
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

def getHostInfo():
    try:
        host_name = socket.gethostname()
        self.ip = socket.gethostbyname(host_name)
        return host_name, self.ip, self.port
    except socket.error:
        print("Unable to get Hostname and/or IP Address")

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
    addresses[client] = client_address
    Thread(target=handle_client, args=(client,)).start()

