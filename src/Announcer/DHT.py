import curio
import logging
import json
from atomicwrites import atomic_write
from util.id import getIdDistance
from Peer.PeerInfo import PeerInfo

MAX_PEER_TABLE_SIZE = 5000

logger = logging.getLogger("DHT")

class DHT:
    def __init__(self, announcer, peer_info):
        self.announcer = announcer
        self.announcer.onAnnounceReceive.subscribe(self.onAnnounceReceive)
        self.self_peer_info = peer_info

        # Load peer table
        self.peer_table = []
        try:
            with open("peer_dht.json") as f:
                table = json.loads(f.read())
            self.peer_table = [PeerInfo.decode(info) for info in table]
        except IOError:
            pass

    async def start(self):
        await curio.spawn(self._saveThread)

    async def _saveThread(self):
        def mapper(val):
            if isinstance(val, PeerInfo):
                return val.encode()
            else:
                raise TypeError("Cannot serialize")

        while True:
            # Save peer table
            with atomic_write("peer_dht.json", overwrite=True) as f:
                f.write(json.dumps(self.peer_table, default=mapper))
            # Sleep for 1 minute
            await curio.sleep(60)

    def onAnnounceReceive(self, new_peer_info):
        if new_peer_info in self.peer_table:
            # Already here, append buckets
            peer_info = self.peer_table[self.peer_table.index(new_peer_info)]
            peer_info.addBuckets(new_peer_info.buckets)
            return

        logger.info(f"Discovered new peer: {new_peer_info}")

        # Check count
        if len(self.peer_table) < MAX_PEER_TABLE_SIZE:
            # Add, doesn't matter what
            self.peer_table.append(new_peer_info)
            return

        # Find the worst peer
        old_peer_info = max(
            self.peer_table,
            key=lambda peer_info: getIdDistance(self.self_peer_info, peer_info)
        )
        # Compare with the new one
        old_dist = getIdDistance(self.self_peer_info, old_peer_info)
        new_dist = getIdDistance(self.self_peer_info, new_peer_info)
        if new_dist < old_dist:
            # Doesn't make sense to add
            return
        # Delete old peer
        self.peer_table.remove(old_peer_info)
        # Add new one
        self.peer_table.append(new_peer_info)