"""
Developers: Braxton Laster, Ben Rader
Desc: Room server for clients to connect to host client
"""

import socket
import threading
import os

# Website with TCP instruction: https://www.thepythoncode.com/article/send-receive-files-using-sockets-python

HEADER_SIZE = 4096  # Chunk size of incoming data
SEPARATOR = '|'  # Used to split sent data into its parts
TRACKER_ADDR = ('127.0.0.1', 5557)  # IP of the tracker server, if running locally needs to be set to own ip


class Server:
    def __init__(self):
        try:
            self.host_name = socket.gethostname()
            self.ip = socket.gethostbyname(self.host_name)
        except socket.error:
            pass

        self.room_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tracker_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 5558
        self.shutdown_flag = False

        self.join_key = None
        self.connected_clients = []
        self.local_directory = 'server_music\\'

    def start(self):
        self.room_server.bind((self.ip, self.port))
        self.room_server.listen()

        self.addServerTracker()
        self.connectionListener()

    # Tells the tracker server a new room has been made along with what port its listening for, receives a join_key back
    def addServerTracker(self):
        self.tracker_server.sendto(('|' + str(self.port)).encode('UTF-8'), TRACKER_ADDR)
        join_key, tracker = self.tracker_server.recvfrom(1024)

        self.join_key = join_key.decode('UTF-8')

    # Continuously listens for new connections, gives each connection a thread and starts an instance of clientWorker
    def connectionListener(self):
        while not self.shutdown_flag:
            client_socket = None
            client_addr = None

            # Need exception otherwise throws error on shutdown due to how sockets and threads are closed
            try:
                client_socket, client_addr = self.room_server.accept()
            except socket.error:
                pass

            self.connected_clients.append((client_socket, client_addr))
            threading.Thread(target=self.clientWorker, args=[self.connected_clients]).start()

    # Receives data from assigned socket, parses it and then sends it to other connected sockets
    def clientWorker(self, connected_clients):
        client_socket, client_addr = connected_clients[-1]

        while not self.shutdown_flag:
            song_header = client_socket.recv(HEADER_SIZE)

            if not song_header:
                break

            file_name, file_size = song_header.decode('utf-8').split(SEPARATOR)
            file_size = int(file_size)

            if not os.path.exists(self.local_directory):
                os.makedirs(self.local_directory)

            song_file = open(self.local_directory + file_name, 'wb')
            song_data = client_socket.recv(HEADER_SIZE)
            download_progress = HEADER_SIZE

            # Make sure all of the file is downloaded to the server before sending to other sockets
            while download_progress < file_size:
                song_file.write(song_data)
                song_data = client_socket.recv(HEADER_SIZE)
                download_progress += HEADER_SIZE
            song_file.close()

            # Sends file to all clients at once rather than 1 at a time
            threads = []
            for (other_soc, other_addr) in self.connected_clients:
                if (other_soc, other_addr) != (client_socket, client_addr):
                    threads.append(threading.Thread(target=self.sendFile, args=(other_soc, file_name)))
                    threads[-1].start()

            for thread in threads:
                thread.join()

        self.connected_clients.remove((client_socket, client_addr))

    def sendFile(self, client_socket, file_name):
        # Rechecks size of file due to some discrepancy from the source file sent from socket
        song_size = os.path.getsize(self.local_directory + file_name)
        song_header = bytes('{}{}{}'.format(file_name, SEPARATOR, song_size), 'utf-8')
        client_socket.send(song_header)

        song_file = open(self.local_directory + file_name, 'rb')
        chunk = song_file.read(HEADER_SIZE)

        while chunk:
            client_socket.send(chunk)
            chunk = song_file.read(HEADER_SIZE)
        song_file.close()

    def shutdown(self):
        self.shutdown_flag = True
        self.room_server.close()
