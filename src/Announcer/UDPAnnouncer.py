import struct
import curio
import random
import logging
from util.Event import Event
from Peer.PeerInfo import PeerInfo

logger = logging.getLogger("UDPAnnouncer")

MAX_BUCKETS = 14
NO_BUCKET = b"\x00" * 32

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
            for i in range(0, len(self.peer_info.buckets), MAX_BUCKETS):
                buckets = self.peer_info.buckets[i:i + MAX_BUCKETS]
                while len(buckets) < MAX_BUCKETS:
                    buckets.append(NO_BUCKET)
                packet = struct.pack(
                    "!8sH32s" + "32s" * MAX_BUCKETS,
                    b"MAGENTA!",
                    tcp_port,
                    network_id,
                    *buckets
                )
                await self.con_man.broadcast(packet)
                curio.sleep(1)
            # Sleep for approx. 30 sec
            time = 25 + random.randint(0, 10)
            await curio.sleep(time)

    def onMessage(self, message, ip, udp_port):
        try:
            unpacked = struct.unpack("!8sH32s" + "32s" * MAX_BUCKETS, message)
            marker, tcp_port, network_id = unpacked[:3]
            if marker != b"MAGENTA!":
                return

            buckets = [bucket for bucket in unpacked[3:] if bucket != NO_BUCKET]

            # Avoid loopbacks
            if network_id != self.peer_info.id:
                peer_info = PeerInfo(
                    ip=ip, tcp_port=tcp_port,
                    id=network_id,
                    buckets=buckets
                )
                self.onAnnounceReceive(peer_info)
        except struct.error:
            # Not for us
            return
        except Exception:
            logger.exception("Got error while handling UDP packet")