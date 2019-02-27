import base64

class PeerInfo:
    def __init__(self, *, ip, tcp_port, id):
        self.ip = ip
        self.tcp_port = tcp_port
        self.id = id

    def __str__(self):
        id_text = "".join((hex(b)[2:].zfill(2) for b in self.id[:6]))
        return f"{self.ip}:{self.tcp_port} (#{id_text}...)"

    # For serialization:
    def encode(self):
        return (self.ip, self.tcp_port, base64.b64encode(self.id).decode())

    @classmethod
    def decode(cls, tp):
        return PeerInfo(tp[0], tp[1], base64.b64decode(tp[2]))

    def toTuple(self):
        return (self.ip, self.tcp_port, self.id)

    def __eq__(self, other):
        return self.toTuple() == other.toTuple()
    def __ne__(self, other):
        return self.toTuple() != other.toTuple()