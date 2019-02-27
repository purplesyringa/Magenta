import struct
import curio
import random
import logging
from util.Event import Event
from Peer.PeerInfo import PeerInfo

logger = logging.getLogger("UDPAnnouncer")

class UDPAnnouncer:
    def __init__(self, con_man, peer_info):
        # Managers
        self.con_man = con_man
        self.peer_info = peer_info
        # Events
        self.onAnnounceReceive = Event("onAnnounceReceive")
        self.con_man.onMessage.subscribe(self.onMessage)

    async def start(self):
        await curio.spawn(self._announcer)

    async def _announcer(self):
        while True:
            tcp_port = self.con_man.tcp.port
            network_id = self.peer_info.id
            # Announce via UDP
            packet = struct.pack("!8sH32s", b"MAGENTA!", tcp_port, network_id)
            await self.con_man.broadcast(packet)
            # Sleep for approx. 30 sec
            time = 25 + random.randint(0, 10)
            await curio.sleep(time)

    def onMessage(self, message, ip, udp_port):
        try:
            marker, tcp_port, network_id = struct.unpack("!8sH32s", message)
            if marker != b"MAGENTA!":
                return
            # Avoid loopbacks
            if network_id != self.peer_info.id:
                peer_info = PeerInfo(ip=ip, tcp_port=tcp_port, id=network_id)
                self.onAnnounceReceive(peer_info)
        except struct.error:
            # Not for us
            return
        except Exception:
            logger.exception("Got error while handling UDP packet")