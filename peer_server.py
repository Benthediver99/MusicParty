"""
Developers: Braxton Laster, Ben Rader
Desc: Server for P2P music streamer, stores ip's of running
"""

import socket
import threading
from random import randint

# Stores list of created room servers with a random code as the key and the addr as the value
room_instances = {}

host_name = socket.gethostname()
ip = socket.gethostbyname(host_name)
port = 5555
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind((ip, port))
shutting_down = False


def newTrackerListener():
    global shutting_down
    while not shutting_down:
        client_data, client_addr = server.recv(1024)
        client_data.decode('UTF-8')

        if '|' in client_data:
            join_key = createKey()
            room_instances.update({join_key : client_addr})
            server.sendto(join_key, client_addr)
        else:
            if client_data in room_instances:
                server.sendto(room_instances.get(client_data), client_addr)


def createKey():
    key = randint(1000, 9999)

    while key in room_instances.keys():
        key = randint(1000, 9999)
    return key


def findRoom(join_key):
    if join_key in room_instances:
        return room_instances.get(join_key)
    else:
        return False


def shutdown(running=True):
    global shutting_down
    shutting_down = running


if __name__ == '__main__':
    tracker_thread = threading.Thread(target=newTrackerListener).start()
