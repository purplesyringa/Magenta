from curio import tcp_server
from util.Event import Event

class TCPUnicastTunnel:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.onMessage = Event("onMessage")
        self.onClose = Event("onClose")
        self.closed = False
        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    async def connect(self):
        await self.sock.connect()

    async def send(self, message):
        if not self.closed:
            await self.sock.send(message)

    async def close(self):
        self.closed = True
        self.onClose()
        await self.sock.shutdown(socket.SHUT_RDWR)
        await self.sock.close()