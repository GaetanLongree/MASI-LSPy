# here is the gestion of hello packet
from scapy.all import *
from data_structures import *
from datetime import datetime, timedelta

entier = 0


def sendHello():
    print("update")
    for key, value in neighborsTable.table.items():
        msg = 'HELLO ' + config.routerName + ' ' + value.name
        print(msg)
        packet = IP(dst=value.ipAddress) / UDP(sport=config.routerPort,
                                              dport=value.port) / Raw(load=msg)
        print(packet)
        # send(packet)


def sendLSAck(dstIP, dstPort, lspSenderName, seqNbr):
    try:
        msg = "LSACK " + config.routerName + " " + lspSenderName + " " + str(seqNbr)
        packet = IP(dst=dstIP)/UDP(sport=config.routerPort, dport=dstPort)/Raw(load=msg)
        #print(msg) #debug
        send(packet)

def gestionOfLSDU(config):
    while True:
        # vérifier que le temps de lastcontact dans l'adjency est plus petit que
        # le 4* hellotimer si c'est good envoyé  et insérer lsuSent sinon pas
        print("BEGINING OF LSDU Gestion")
        # print(config.maxLSPDelay)
        payload = generatePayloadLSDU(config)
        for k in adjacencyTable.table:
            x = adjacencyTable.table[k]
            # print(x.lastContact.strftime("%Y-%m-%d %H:%M:%S") + "----" +
            #      (datetime.utcnow() + timedelta(seconds=4 * config.helloDelay)).strftime("%Y-%m-%d %H:%M:%S"))
            if (x.lastContact <= (datetime.utcnow() + timedelta(seconds=4 * config.helloDelay))):
                packet = (IP(dst=x.ipAddress) / UDP(sport=config.routerPort,
                                                    dport=x.port) / Raw(load=payload))
                # send(packet)
                # print("LSDU")
                # packet.show()
        time.sleep(config.maxLSPDelay)


def generatePayloadLSDU(config):
    # messagesis:LSP[SenderName][SequenceNumber][AdjacentActive Links].
    global entier
    payload = "LSP " + config.routerName + " " + str(entier % 100) + " "
    for k in neighborsTable.table:
        payload += neighborsTable.table[k].name + \
            " " + neighborsTable.table[k].linkCost + " "
    entier += 1
    print("payload of LSDU produce : " + payload)
    return payload[:-1]


def forwardLSDUToNeighbor(payload, routerName):
    # (payload,nom du routeur de qui je viens de le
    # recevoir)(tous sauf celui qui vient de me l'envoyer) demandé par gaetan
    for k in adjacencyTable.table:
        x = adjacencyTable.table[k]
        if(k == routerName):
            pass
        else:
            packet = (IP(dst=x.ipAddress) / UDP(sport=config.routerPort,
                                                dport=x.port) / Raw(load=payload))
    # send(packet)
    print("Forward LSDUToNeighbor")
    packet.show()
