# here is the gestion of hello packet
from scapy.all import *
from data_structures import *

def sendHello():
    print("update")
    for key, value in neighborsTable.table.items():
        msg = 'HELLO ' + config.routerName + ' ' +value.name
        print(msg)
        packet = IP(dst=value.ipAddress / UDP(sport=config.routerName,
                                       dport=value.port) / Raw(load=msg))
        print(packet)
        # send(packet)


def sendLSAck():
    x = 0


def sendLSDU():
    x = 0


def forwardLSDUToNeihbors():
    x = 0
