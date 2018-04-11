# here is the gestion of hello packet
from scapy.all import *
from server import neighbor
# [0]name [1]ip address [2]port [3]priority

# for hello packet = https://brownian.org.ua/?p=140&langswitch_lang=en
load_contrib('ospf')

HELLO_DELAY = 5000
NB_Neigh = 4


def update():
    print("update")
    for nb in NB_Neigh:
        packet = Ether() / IP(dst=neighbor[NB_Neigh][1]) / OSPF()
        recive = srp(packet)
    time.sleep(5)
    for c in receive:
        # receive[c][1] les réponses des packets envoyés
        une_reponse = recive[c][1]


# constructor
def __init__(self, arg, arg_1):
    self.arg = arg
    self.arg_1 = arg_1
