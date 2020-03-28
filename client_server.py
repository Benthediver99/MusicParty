"""
Developers: Braxton Laster, Ben Rader
Desc: client server for clients to connect to host client
"""

import socket
import threading

# Website with TCP instruction: https://www.thepythoncode.com/article/send-receive-files-using-sockets-python

HEADER_SIZE = 1024
SEPARATOR = '|'
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
        self.port = 5558
        self.shutdown = False

        self.join_key = None
        self.connected_clients = []

    def start(self):
        self.room_server.bind((self.ip, self.port))
        self.room_server.listen()

        self.addServerTracker()
        self.connectionListener()

    def addServerTracker(self):
        self.tracker_server.sendto(('|' + str(self.port)).encode('UTF-8'), TRACKER_ADDR)
        join_key, tracker = self.tracker_server.recvfrom(1024)

        self.join_key = join_key.decode('UTF-8')

    def connectionListener(self):
        print('Running connection listener...')
        while True:
            print('Back to waiting...')
            client_socket, client_addr = self.room_server.accept()

            self.connected_clients.append((client_socket, client_addr))
            threading.Thread(target=self.clientWorker, args=[self.connected_clients]).start()

    def clientWorker(self, connected_clients):
        client_socket, client_addr = connected_clients[-1]
        print('Client {} running worker...'.format(client_addr))

        while not self.shutdown:
            new_song = True
            while True:
                song_data = client_socket.recv(HEADER_SIZE)

                if not song_data:
                    print("Client disconnect")
                    break
                elif new_song:
                    print("new msg len:", song_data[:HEADER_SIZE])
                    msglen = int(msg[:HEADER_SIZE])

                    file_name, file_size = song_data.decode('utf-8').split(SEPARATOR)
                    print('Name: {} Size: {}'.format(file_name, file_size))
                    new_msg = False

                print(f"full message length: {msglen}")

                print("Got: {}".format(msg))
                msg = msg.decode('ascii')
                for other_soc, other_addr in self.connected_clients:
                    if (client_socket, client_addr) != (other_soc, other_addr):
                        print("Sending to {}".format(other_addr))
                        other_soc.sendall(msg.encode('ascii'))
            self.connected_clients.remove((client_socket, client_addr))

    def shutdown(self):
        self.shutdown = True
        self.room_server.close()

        for thread in self.threads:
            thread.join()
