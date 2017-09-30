

import struct
import socket
import random
import binascii


from os import getpid, urandom
from pycomm.cip.cip_const import *
from pycomm.common import PycommError


class CommError(PycommError):
    pass


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((socket.gethostname(), 44818))
sock.listen(5)


# while True:
#     # accept connections from outside
#     (clientsocket, address) = serversocket.accept()
#     # now do something with the clientsocket
#     # in this case, we'll pretend this is a threaded server
#     ct = client_thread(clientsocket)
#     ct.run()


msg_len = 28
chunks = []
bytes_recd = 0
one_shot = True
con, addr = sock.accept()
while True:
    while bytes_recd < msg_len:
        try:
            chunk = con.recv(min(msg_len - bytes_recd, 2048))
            print(addr)
            if chunk == '':
                raise CommError("socket connection broken.")
            if one_shot:
                data_size = int(struct.unpack('<H', chunk[2:4])[0])  # Length
                msg_len = HEADER_SIZE + data_size
                one_shot = False

            chunks.append(chunk)
            bytes_recd += len(chunk)
        except socket.error as e:
            raise CommError(e)
    msg = b''.join(chunks)
    hexVersion = msg.hex()
    print(binascii.unhexlify(hexVersion))
