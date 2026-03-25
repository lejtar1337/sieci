import sys

def print_ip(label, ip):
    dec = f"{(ip >> 24) & 255}.{(ip >> 16) & 255}.{(ip >> 8) & 255}.{ip & 255}"
    bin_str = f"{(ip >> 24) & 255:08b}.{(ip >> 16) & 255:08b}.{(ip >> 8) & 255:08b}.{ip & 255:08b}"
    print(f"{label+':':<18} {dec:<15} | {bin_str}")

try:
    ip_str, cidr_str = sys.argv[1].split('/')
    cidr = int(cidr_str)    
    p = list(map(int, ip_str.split('.')))
    ip32 = (p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]
except ValueError:
    print("py lol.py 192.168.0.0/24")
    sys.exit(1)

mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
network = ip32 & mask
broadcast = network | (~mask & 0xFFFFFFFF)
hosts = (1 << (32 - cidr)) - 2 if cidr < 31 else 0

print_ip("Adres sieci", network)
print_ip("Maska", mask)
print(f"{'Ilość hostów:':<18} {hosts}")
print_ip("Pierwszy host", network + 1 if hosts > 0 else network)
print_ip("Ostatni host", broadcast - 1 if hosts > 0 else broadcast)
print_ip("Broadcast", broadcast)
