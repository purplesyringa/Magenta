from Transport.ConnectionManager import ConnectionManager
import curio

async def main():
    print("Welcome!")
    print("--------")

    udp_port = int(input("UDP port: "))
    tcp_port = int(input("TCP port: "))
    nickname = input("Your name: ")

    conn = ConnectionManager(udp_port, tcp_port)

    await conn.start()
    print("Listening...")

    def onMessage(message, ip, port):
        print(message.decode("utf8"), f"    (from {ip}:{port})", sep="")
    conn.onMessage.subscribe(onMessage)

    try:
        while True:
            message = (await curio.run_in_thread(input)).replace("\r", "")
            await conn.broadcast(f"{nickname}: {message}".encode("utf8"))
    except KeyboardInterrupt:
        print("Exitting...")
        await conn.close()

curio.run(main)