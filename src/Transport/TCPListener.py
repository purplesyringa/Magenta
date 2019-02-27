import curio
from curio import socket, tcp_server
from util.Event import Event

class TCPListener:
    def __init__(self, port):
        self.port = port
        self.onMessage = Event("onMessage")
        self.onClose = Event("onClose")
        self.closed = False
        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", self.port))
        self.sock.listen()

    async def listen(self):
        while not self.closed:
            conn, (ip, port) = await self.sock.accept()
            await curio.spawn(self._connectionHandler, conn, ip, port)

    async def _connectionHandler(self, conn, ip, port):
        message = ""
        while True:
            part = conn.recv(1024)
            if not part:
                break
            message += part

        self.onMessage(message, ip, port)

    async def close(self):
        self.closed = True
        self.onClose()
        await self.sock.shutdown(socket.SHUT_RDWR)
        await self.sock.close()