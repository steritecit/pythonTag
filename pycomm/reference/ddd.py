    def connect(self, host, port):
        try:
            self.sock.connect((host, port))
        except socket.timeout:
            raise CommError("Socket timeout during connection.")

    def send(self, msg, timeout=0):
        if timeout != 0:
            self.sock.settimeout(timeout)
        total_sent = 0
        while total_sent < len(msg):
            try:
                sent = self.sock.send(msg[total_sent:])
                if sent == 0:
                    raise CommError("socket connection broken.")
                total_sent += sent
            except socket.error:
                raise CommError("socket connection broken.")
        return total_sent