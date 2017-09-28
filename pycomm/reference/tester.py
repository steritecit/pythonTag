
import struct
import socket
import random
# import binascii
# from scapy.all import *
# import cip

# from os import getpid, urandom
# from pycomm.cip.cip_const import *
# from pycomm.common import PycommError

import SocketServer


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


if __name__ == "__main__":
    HOST, PORT = "localhost", 44818

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


# class CommError(PycommError):


# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.bind((socket.gethostname(), 44818))
# sock.listen(5)


# while True:
#     # accept connections from outside
#     (clientsocket, address) = serversocket.accept()
#     # now do something with the clientsocket
#     # in this case, we'll pretend this is a threaded server
#     ct = client_thread(clientsocket)
#     ct.run()

# msg_len = 28
# chunks = []
# bytes_recd = 0
# one_shot = True
# con, addr = sock.accept()


# while True:
#     print 'here'
    # while bytes_recd < msg_len:

    #     chunk = con.recv(min(msg_len - bytes_recd, 2048))
    #     print addr
    #     if one_shot:
    #         data_size = int(struct.unpack('<H', chunk[2:4])[0])  # Length
    #         msg_len = 24 + data_size
    #         one_shot = False

    #     chunks.append(chunk)
    #     bytes_recd += len(chunk)

    #     msg = b''.join(chunks)
