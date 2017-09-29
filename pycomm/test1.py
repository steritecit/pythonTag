# import select
# import socket

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server_socket.bind(('localhost', 45000))
# server_socket.listen(5)
# print "Listening on port 45000"


# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket, address = server_socket.accept()
# read_list = [server_socket]
# while True:
#     readable, writable, errored = select.select(read_list, [], [])
#     for s in readable:
#         if s is server_socket:
#             read_list.append(client_socket)
#             print "Connection from", address
#         else:
#             data = s.recv(1024)
#             if data:
#                 s.send(data)
#             else:
#                 s.close()
#                 read_list.remove(s)
import socket
import time
import struct
# from scapy.all import *
# import cip


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket
host = socket.gethostname()  # Get local machine name
port = 44818                # Reserve a port for your service.
s.bind(('', port))        # Bind to the port

s.listen(5)
c, addr = s.accept()     # Establish connection with client.
print 'Got connection from', addr

msg_len = 82
chunks = []
bytes_recd = 0
one_shot = True


while bytes_recd < msg_len:

    chunk = c.recv(min(msg_len - bytes_recd, 2048))
    print addr
    if one_shot:
        data_size = int(struct.unpack('<H', chunk[2:4])[0])  # Length
        msg_len = 24 + data_size
        one_shot = False

    print chunk

    chunks.append(chunk)
    bytes_recd += len(chunk)

    msg = ''.join(chunks)

# print chunks[0].decode(encoding='utf-8')

print struct.unpack(chunks[0])
