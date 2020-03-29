"""
Developers: Braxton Laster, Ben Rader
Desc: Server for P2P music streamer, stores ip's of running
"""

import socket
import threading
import pickle
from random import randint

# Stores list of created room servers with a random code as the key and the addr as the value
room_instances = {}

host_name = socket.gethostname()
ip = socket.gethostbyname(host_name)
port = 5557
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print('Tracker Address: {}:{}'.format(ip, port))

server.bind((ip, port))
shutting_down = False


# Uses UDP for sockets to find what server address they need to establish TCP connection with
def newTrackerListener():
    global shutting_down
    global room_instances

    while not shutting_down:
        print('Rooms: {}'.format(room_instances))
        client_data, client_addr = server.recvfrom(1024)
        client_data = client_data.decode('UTF-8')

        # Pipe key used to distinguish new host from socket trying to join a server
        if '|' in client_data:
            print('New host...')
            join_key = createKey()

            room_port = client_data.split('|')
            room_port = int(room_port[1])

            # Adds server address to dictionary w/ a random join_key associated with it
            room_instances.update({join_key: (client_addr[0], room_port)})
            print('Room Key is: {}'.format(join_key))
            server.sendto(join_key.encode('UTF-8'), client_addr)
        else:
            # If join_key found, return server address to socket that requested it
            if client_data in room_instances.keys():
                print('Room {} found'.format(client_data))
                server.sendto(pickle.dumps(room_instances.get(client_data)), client_addr)


# Returns a random 4 digit code that will be associated with a server address for other clients to connect with
def createKey():
    key = randint(1000, 9999)

    # Prevents duplicate keys from popping up
    while key in room_instances.keys():
        key = randint(1000, 9999)
    return str(key)


def shutdown(running=True):
    global shutting_down
    shutting_down = running


tracker_thread = threading.Thread(target=newTrackerListener).start()
