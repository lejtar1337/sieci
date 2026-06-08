import socket, threading, json

def receive_messages(sock):
    stream = sock.makefile('r')
    try:
        for line in stream:
            data = json.loads(line)
            if "status" in data:
                print(f"[Serwer] {data}")
            elif data["type"] == "info":
                print(f"[System] {data['msg']}")
            else:
                tag = "[Priv]" if data.get("type") == "priv" else "[All]"
                print(f"{tag} {data['from']}: {data['msg']}")
    except:
        print("Rozłączono.")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 5555))
threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

print("Komendy: /reg <user> <haslo> | /log <user> <haslo> | /all <wiadomosc> | /msg <user> <wiadomosc>")
while True:
    try:
        cmd = input().split(" ", 1)
        if not cmd or not cmd[0]: continue
        
        if cmd[0] == "/reg":
            u, p = cmd[1].split(" ", 1)
            sock.sendall((json.dumps({"action": "register", "user": u, "password": p}) + "\n").encode())
        elif cmd[0] == "/log":
            u, p = cmd[1].split(" ", 1)
            sock.sendall((json.dumps({"action": "login", "user": u, "password": p}) + "\n").encode())
        elif cmd[0] == "/all":
            sock.sendall((json.dumps({"action": "broadcast", "msg": cmd[1]}) + "\n").encode())
        elif cmd[0] == "/msg":
            u, msg = cmd[1].split(" ", 1)
            sock.sendall((json.dumps({"action": "private", "to": u, "msg": msg}) + "\n").encode())
    except Exception:
        print("Błędny format komendy.")