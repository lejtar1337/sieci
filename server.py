import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', 9999))
clients = {}

while True:
    data, addr = server_socket.recvfrom(1024)
    
    if not data:
        clients.pop(addr, None)
        continue
    
    prefix = data[:1]
    content = data[1:]
    
    if prefix == b'\0':
        clients[addr] = content.decode()
    elif prefix == b'\1' and addr in clients:
        msg = f"{clients[addr]}: {content.decode()}".encode()
        for client_addr in clients:
            if client_addr != addr:
                server_socket.sendto(msg, client_addr)