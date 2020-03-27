import socket
import pickle
import threading
import os

# Website with TCP instruction: https://www.thepythoncode.com/article/send-receive-files-using-sockets-python

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024
TRACKER_ADDR = ('192.168.4.53', 5557)


class Server:
    def __init__(self):
        try:
            self.host_name = socket.gethostname()
            self.ip = socket.gethostbyname(self.host_name)
        except socket.error:
            pass

        self.room_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tracker_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 5555
        self.shutdown = False

        self.join_key = None
        self.connected_clients = []
        self.threads = []

    def start(self, ip_address=None, port=None):
        if ip_address is not None and port is not None:
            self.ip = ip_address
            self.port = port
            self.room_server.bind((ip_address, port))
        else:
            self.room_server.bind((self.ip, self.port))
        self.room_server.listen()

        self.addServerTracker()
        self.connectionListener()

    def addServerTracker(self):
        self.tracker_server.sendto('|'.encode('UTF-8'), TRACKER_ADDR)
        join_key, tracker = self.tracker_server.recvfrom(1024)

        self.join_key = join_key.decode('UTF-8')

    def connectionListener(self):
        while True:
            client_socket, client_addr = self.room_server.accept()

            if (client_socket, client_addr) not in self.connected_clients:
                self.connected_clients.append((client_socket, client_addr))
                self.threads.append(threading.Thread(target=self.clientWorker()).start())

    def clientWorker(self):
        client_socket, client_addr = self.connected_clients[-1]
        while True:
            pass

    def shutdown(self):
        self.shutdown = True
        self.server.close()
