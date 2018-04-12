# here is the gestion of hello packet
from scapy.all import *
from server import neighbor, ROUTER_NAME, ROUTER_PORT

HELLO_DELAY = 5000
NB_Neigh = 4


def update():
    print("update")
    for nb in NB_Neigh:
        msg = 'HELLO ' + neighbor[NB_Neigh]['name'] + ' ' + ROUTER_NAME
        print(msg)
        packet = IP(dst=neighbor[NB_Neigh][
                    'ip'] / UDP(sport=ROUTER_PORT, dport=neighbor[NB_Neigh]['port']) / Raw(load=msg))
        print(packet)
        send(packet)


if __name__ == "__main__":
    update()
