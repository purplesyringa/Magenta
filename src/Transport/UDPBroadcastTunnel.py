from curio import socket
from util.Event import Event

class UDPBroadcastTunnel:
    def __init__(self, port):
        self.port = port
        self.onMessage = Event("onMessage")
        self.onClose = Event("onClose")
        self.closed = False
        # Create receiver socket
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_sock.bind(("", self.port))
        # Create sender socket
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    async def listen(self):
        while not self.closed:
            message, (ip, port) = await self.recv_sock.recvfrom(1024)
            self.onMessage(message, ip, port)

    async def broadcast(self, message):
        if not self.closed:
            await self.send_sock.sendto(message, ("255.255.255.255", self.port))

    async def close(self):
        self.closed = True
        self.onClose()
        await self.recv_sock.shutdown(socket.SHUT_RDWR)
        await self.recv_sock.close()
        await self.send_sock.shutdown(socket.SHUT_RDWR)
        await self.send_sock.close()