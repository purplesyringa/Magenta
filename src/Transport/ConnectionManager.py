from .UDPBroadcastTunnel import UDPBroadcastTunnel
from .TCPListener import TCPListener
from .TCPUnicastTunnel import TCPUnicastTunnel
from util.Event import Event
import curio

class ConnectionManager:
    def __init__(self, udp_port, tcp_port):
        self.onMessage = Event("onMessage")
        # Create listeners
        self.udp = UDPBroadcastTunnel(udp_port)
        self.tcp_listener = TCPListener(tcp_port)
        # Tunnels
        self.tunnels = {}

    async def start(self):
        # Set up UDP
        self.udp.onMessage.subscribe(lambda *arg: self.onMessage(*arg))
        await curio.spawn(self.udp.listen)
        # Set up TCP
        self.tcp_listener.onMessage.subscribe(lambda *arg: self.onMessage(*arg))
        await curio.spawn(self.tcp_listener.listen)

    async def close(self):
        await self.udp.close()
        await self.tcp_listener.close()
        tunnels = self.tunnels
        self.tunnels.clear()
        for tunnel in tunnels.values():
            await tunnel.close()


    async def send(self, message, ip, port):
        # Send via TCP
        if (ip, port) not in self.tunnels:
            # Open tunnel if not opened already
            self.tunnels[(ip, port)] = TCPUnicastTunnel(ip, port)
            await self.tunnels[(ip, port)].connect()
        # Send message
        await self.tunnels[(ip, port)].send(message)

    async def broadcast(self, message):
        # Send via UDP
        await self.udp.broadcast(message)


    async def closeTunnel(self, ip, port):
        if (ip, port) not in self.tunnels:
            raise KeyError("Tunnel not opened yet")
        tunnel = self.tunnels[(ip, port)]
        del self.tunnels[(ip, port)]
        await tunnel.close()