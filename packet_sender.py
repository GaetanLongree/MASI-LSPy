# here is the gestion of hello packet
from scapy.all import *
from data_structures import *

entier = 0


def gestionOfLSUSent():
    for k in adjacencyTable:
        sendSLU(k)
    time.sleep(4 * config.maxLSPDelay)


def sendSLU(adjacency):
    lSUSent = LSUSentTable.insertLSUSent(
        adjacency, config.routerName, entier % 100, generatePayloadLSDU())
    packet = IP(dst=adjacency.ipAddress) / UDP(sport=config.routerPort,
                                               dport=adjacency.port) / Raw(load=adjacency.payload)
    # send(packet)
    packet.show()
    t = threading.Thread(target=checkSLUTable(lSUSent))
    t.start()


def checkSLUTable(lSUSent):
    for x in range(0, 4):
        if(LSUSentTable.contains(lSUSent)):
            sendSLU(adjacencyTable.contains(lSUSent.routerName))
            time.sleep(config.maxLSPDelay)
        else:
            break


def sendHello():
    print("update")
    for key, value in neighborsTable.items():
        msg = 'HELLO ' + config.routerName + ' ' + value.name
        print(msg)
        packet = IP(dst=value.ipAddress) / UDP(sport=config.routerPort,
                                               dport=value.port) / Raw(load=msg)
        packet.show()
        # send(packet)


def sendLSAck(dstIP, dstPort, lspSenderName, seqNbr):
    msg = "LSACK " + config.routerName + \
        " " + lspSenderName + " " + str(seqNbr)
    packet = IP(dst=dstIP) / UDP(sport=config.routerPort,
                                 dport=dstPort) / Raw(load=msg)
    # print(msg) #debug
    send(packet)


def gestionOfLSDU():
    while True:
        # vérifier que le temps de lastcontact dans l'adjency est plus petit que
        # le 4* hellotimer si c'est good envoyé  et insérer lsuSent sinon pas
        print("BEGINING OF LSDU Gestion")
        # print(config.maxLSPDelay)
        payload = generatePayloadLSDU()
        for k in adjacencyTable:
            x = adjacencyTable[k]
            if(x is not None):
                packet = (IP(dst=x.ipAddress) / UDP(sport=config.routerPort,
                                                    dport=x.port) / Raw(load=payload))
            else:
                print(k + "is gone")
                # send(packet)
                # print("LSDU")
                # packet.show()
        time.sleep(config.maxLSPDelay)


def generatePayloadLSDU():
    # messagesis:LSP[SenderName][SequenceNumber][AdjacentActive Links].
    global entier
    payload = "LSP " + config.routerName + " " + str(entier % 100) + " "
    for k in neighborsTable:
        payload += neighborsTable[k].name + \
            " " + neighborsTable[k].linkCost + " "
    entier += 1
    print("payload of LSDU produce : " + payload)
    return payload[:-1]


def forwardLSDUToNeighbor(payload, routerName):
    # (payload,nom du routeur de qui je viens de le
    # recevoir)(tous sauf celui qui vient de me l'envoyer) demandé par gaetan
    for k in adjacencyTable:
        x = adjacencyTable[k]
        if(k == routerName):
            pass
        else:
            packet = (IP(dst=x.ipAddress) / UDP(sport=config.routerPort,
                                                dport=x.port) / Raw(load=payload))
    # send(packet)
    print("Forward LSDUToNeighbor")
    packet.show()
