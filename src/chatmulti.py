from Transport.ConnectionManager import ConnectionManager
import curio

async def main():
    print("Welcome!")
    print("--------")

    udp_group = input("UDP group: ")
    udp_port = int(input("UDP port: "))
    tcp_port = int(input("TCP port: "))
    nickname = input("Your name: ")

    conn = ConnectionManager(udp_group, udp_port, tcp_port)

    await conn.start()
    print("Listening...")

    def onMessage(message, ip, port):
        print(message.decode("utf8"), f"    (from {ip}:{port})", sep="")
    conn.onMessage.subscribe(onMessage)

    try:
        import msvcrt
        import sys
        while True:
            message = b""
            while b"\r" not in message:
                await curio.sleep(0.001)
                if msvcrt.kbhit():
                    c = msvcrt.getch()
                    sys.stdout.write(c.decode("utf8"))
                    sys.stdout.flush()
                    message += c
            message = message.decode("utf8").replace("\r", "")

            await conn.broadcast(f"{nickname}: {message}".encode("utf8"))
    except KeyboardInterrupt:
        print("Exitting...")
        await conn.close()

curio.run(main)