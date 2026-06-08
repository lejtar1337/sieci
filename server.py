import socket, threading, json

registered_users = {}
active_users = {}
lock = threading.Lock()

def broadcast(msg, sender=None):
    with lock:
        for user, sock in active_users.items():
            if user != sender:
                try: sock.sendall((json.dumps(msg) + "\n").encode())
                except: pass

def handle_client(sock):
    user = None
    stream = sock.makefile('r')
    try:
        for line in stream:
            data = json.loads(line)
            action = data.get("action")

            if action == "register":
                u, p = data["user"], data["password"]
                with lock:
                    if u in registered_users:
                        sock.sendall(b'{"status": "error", "msg": "User exists"}\n')
                    else:
                        registered_users[u] = p
                        sock.sendall(b'{"status": "ok", "msg": "Registered"}\n')
            
            elif action == "login":
                u, p = data["user"], data["password"]
                with lock:
                    if registered_users.get(u) == p and u not in active_users:
                        user = u
                        active_users[u] = sock
                        sock.sendall((json.dumps({"status": "ok", "users": list(active_users.keys())}) + "\n").encode())
                        break
                    else:
                        sock.sendall(b'{"status": "error", "msg": "Login failed"}\n')
        
        if user:
            broadcast({"type": "info", "msg": f"{user} dołączył."}, user)
            for line in stream:
                data = json.loads(line)
                action = data.get("action")
                if action == "broadcast":
                    broadcast({"type": "msg", "from": user, "msg": data["msg"]}, user)
                elif action == "private":
                    target = data.get("to")
                    with lock:
                        if target in active_users:
                            active_users[target].sendall((json.dumps({"type": "priv", "from": user, "msg": data["msg"]}) + "\n").encode())

    except Exception:
        pass
    finally:
        if user:
            with lock:
                if user in active_users: del active_users[user]
            broadcast({"type": "info", "msg": f"{user} rozłączył się."})
        sock.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.0", 5555))
server.listen()
while True:
    client, _ = server.accept()
    threading.Thread(target=handle_client, args=(client,), daemon=True).start()