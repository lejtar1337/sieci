import socket
import select
import sys

SERVER_ADDR = ('127.0.0.1', 9999)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setblocking(False)

nickname = input("Podaj nickname: ")
client_socket.sendto(b'\0' + nickname.encode(), SERVER_ADDR)

while True:
    readable, _, _ = select.select([client_socket, sys.stdin], [], [])
    
    for s in readable:
        if s is client_socket:
            data, _ = client_socket.recvfrom(1024)
            print(data.decode())
        elif s is sys.stdin:
            msg = sys.stdin.readline().strip()
            if not msg:  # Pusty Enter lub EOF wysyła sygnał rozłączenia
                client_socket.sendto(b'', SERVER_ADDR)
                sys.exit(0)
            client_socket.sendto(b'\1' + msg.encode(), SERVER_ADDR)