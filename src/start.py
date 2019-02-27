import logging
import chalk
import configparser
import random
import curio
from Transport.ConnectionManager import ConnectionManager
from Peer.PeerInfo import PeerInfo
from Announcer.UDPAnnouncer import UDPAnnouncer
from Announcer.DHT import DHT

async def main():
    # Init logging
    format_str = "{asctime} | {levelname} | {module} | {message}".format(
        asctime=chalk.bold(chalk.cyan("{asctime}")),
        levelname=chalk.bold(chalk.red("{levelname:8}")),
        module=chalk.bold(chalk.green("{module:12}")),
        message=chalk.bold("{message}")
    )
    logging.basicConfig(format=format_str, style="{", level=logging.INFO)


    logging.info("Reading config")
    config = configparser.ConfigParser()
    config.read("magenta.ini")

    logging.info("Starting MAGENTA")
    udp_port = int(config["Internet"]["udp_port"])
    if "tcp_port" not in config["Internet"]:
        # Generate TCP port randomly
        config["Internet"]["tcp_port"] = str(random.randint(60000, 65535))
        # Save to config
        with open("magenta.ini", "w") as f:
            config.write(f)
    tcp_port = int(config["Internet"]["tcp_port"])

    logging.info("Creating connection manager")
    con_man = ConnectionManager(udp_port, tcp_port)
    await con_man.start()

    logging.info("Creating peer info")
    network_id = bytes((random.randint(0, 255) for _ in range(32)))
    peer_info = PeerInfo(ip="127.0.0.1", tcp_port=tcp_port, id=network_id)

    logging.info("Creating UDP announcer")
    udp_announcer = UDPAnnouncer(con_man, peer_info)
    await udp_announcer.start()

    logging.info("Creating DHT")
    dht = DHT(udp_announcer, peer_info)
    await dht.start()

    while True:
        await curio.sleep(1000)

curio.run(main)