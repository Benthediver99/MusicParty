"""
Developers: Braxton Laster, Ben Rader
Desc: Server for P2P music streamer, stores ip's of running
"""

import socket


def shutdownServer(running=True):
    global shutting_down
    shutting_down = running


# Stores list of created room servers with a random code as the key and the addr as the value
room_instances = {}

host_name = socket.gethostname()
ip = socket.gethostbyname(host_name)
port = 5555
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(ip, port)

shutting_down = False
while not shutting_down:
    client_data, client_addr = server.recv(1024)

    if '|' in client_data:
        join_key = client_data.split('|', 1)
        room_instances.update({join_key : client_addr})
    else:
        if client_data in room_instances:
            server.sendto(room_instances.get(client_data), client_addr)






