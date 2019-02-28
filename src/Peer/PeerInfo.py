import base64

def b64encode(value):
    return base64.b64encode(value).decode()

b64decode = base64.b64decode

class PeerInfo:
    def __init__(self, *, ip, tcp_port, id, buckets):
        self.ip = ip
        self.tcp_port = tcp_port
        self.id = id
        self.buckets = buckets

    def __str__(self):
        id_text = "".join((hex(b)[2:].zfill(2) for b in self.id[:6]))
        return f"{self.ip}:{self.tcp_port} (#{id_text}...)"

    # For serialization:
    def encode(self):
        return (
            self.ip,
            self.tcp_port,
            b64encode(self.id),
            list(map(b64encode, buckets))
        )

    @classmethod
    def decode(cls, tp):
        return PeerInfo(
            ip=tp[0],
            tcp_port=tp[1],
            id=base64.b64decode(tp[2]),
            buckets=set(map(b64decode, tp[3]))
        )

    def toTuple(self):
        return (self.ip, self.tcp_port, self.id)


    def addBuckets(self, buckets):
        for bucket in buckets:
            self.buckets.add(bucket)


    def __eq__(self, other):
        return self.toTuple() == other.toTuple()
    def __ne__(self, other):
        return self.toTuple() != other.toTuple()