# here is the gestion of hello packet
from scapy.all import *
from data_structures import *
import threading
import datetime

class HelloHandlerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stopThread = threading.Event()

    def sendHello(self):
        #print("Sending HELLO message" # debug)
        for key, value in neighborsTable.items():
            msg = 'HELLO ' + config.routerName + ' ' + value.name
            #print(msg) # debug
            packet = IP(dst=value.ipAddress) / UDP(sport=config.routerPort, dport=int(value.port)) / Raw(load=msg)
            #packet.show() # debug
            send(packet, verbose=False)

    def run(self):
        while self.stopThread.isSet() is not True:
            time.sleep(config.helloDelay)
            self.sendHello()

    def stop(self, timeout=None):
        self.stopThread.set()
        super().join(timeout)


class LSUHandlerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stopThread = threading.Event()

    def generatePayloadLSDU(self):
        # messagesis:LSP[SenderName][SequenceNumber][AdjacentActive Links].
        payload = "LSP " + config.routerName + " " + str(config.seqNbrInt % 100) + " "
        for k in neighborsTable:
            payload += neighborsTable[k].name + \
                " " + neighborsTable[k].linkCost + " "
        config.seqNbrInt += 1
        #print("payload of LSDU produce : " + payload)
        return payload[:-1]

    def run(self):
        #print("BEGINING OF LSDU Gestion")
        while self.stopThread.isSet() is not True:
            # print(config.maxLSPDelay)
            payload = self.generatePayloadLSDU()
            adjacencyTable.acquire()
            for k in adjacencyTable:
                adjacency = adjacencyTable[k]
                if(adjacency is not None):
                    lSUSentTable.acquire()
                    lsuSent = lSUSentTable.insertLSUSent(adjacency.name, config.routerName, (config.seqNbrInt%100) , payload)
                    lSUSentTable.release()
                    packet = IP(dst=adjacency.ipAddress) / UDP(sport=config.routerPort, dport=adjacency.port) / Raw(load=lsuSent.payload)
                    send(packet, verbose=False)
                    lsuSentHandlerThreads.acquire()
                    lsuSentHandlerThreads.append(LSUSentHandlerThread(lsuSent))
                    lsuSentHandlerThreads[-1].start()
                    lsuSentHandlerThreads.release()
                    # packet.show() # debug
            adjacencyTable.release()
            time.sleep(config.maxLSPDelay)

    def stop(self, timeout=5):
        self.stopThread.set()
        for thread in lsuSentHandlerThreads:
            thread.stop(5)
        if adjacencyTable.lock.locked() == True:
            adjacencyTable.release()
        if lSUSentTable.lock.locked() == True:
            lSUSentTable.release()
        if lsuSentHandlerThreads.lock.locked() == True:
            lsuSentHandlerThreads.release()
        super().join(timeout)


class LSUSentHandlerThread(threading.Thread):
    def __init__(self, lsuSent):
        threading.Thread.__init__(self)
        self.stopThread = threading.Event()
        self.lsuSent = lsuSent

    def run(self):
        for x in range(0, 4):
            time.sleep(5)
            if self.stopThread.isSet() is True:
                break
            if(lSUSentTable.contains(self.lsuSent.routerName, self.lsuSent.lspSourceName, self.lsuSent.sequenceNumber)):
                adjacencyTable.acquire()
                adjacency = adjacencyTable[self.lsuSent.routerName]
                adjacencyTable.release()
                if adjacency is not None:
                    packet = IP(dst=adjacency.ipAddress) / UDP(sport=config.routerPort, dport=adjacency.port) / Raw(load=self.lsuSent.payload)
                    send(packet, verbose=False)
            else:
                break

    def stop(self, timeout=None):
        self.stopThread.set()
        if adjacencyTable.lock.locked() == True:
            adjacencyTable.release()
        if lSUSentTable.lock.locked() == True:
            lSUSentTable.release()
        super().join(timeout)



def sendLSAck(dstIP, dstPort, lspSenderName, seqNbr):
    msg = "LSACK " + config.routerName + \
        " " + lspSenderName + " " + str(seqNbr)
    packet = IP(dst=dstIP) / UDP(sport=config.routerPort,
                                 dport=dstPort) / Raw(load=msg)
    # print(msg) #debug
    send(packet, verbose=False)


def forwardLSDUToNeighbor(payload, routerName, seqNbr):
    # (payload,nom du routeur de qui je viens de le
    # recevoir)(tous sauf celui qui vient de me l'envoyer) demandé par gaetan
    adjacencyTable.acquire()
    for k in adjacencyTable:
        adjacency = adjacencyTable[k]
        if adjacency != None and k != routerName:
            lSUSentTable.acquire()
            lsuSent = lSUSentTable.insertLSUSent(adjacency.name, routerName, seqNbr , payload)
            lSUSentTable.release()
            packet = IP(dst=adjacency.ipAddress) / UDP(sport=config.routerPort, dport=adjacency.port) / Raw(load=lsuSent.payload)
            send(packet, verbose=False)
            lsuSentHandlerThreads.acquire()
            lsuSentHandlerThreads.append(LSUSentHandlerThread(lsuSent))
            lsuSentHandlerThreads[-1].start()
            lsuSentHandlerThreads.release()
            # packet.show() # debug
    adjacencyTable.release()
    #print("Forward LSDUToNeighbor")
    #packet.show() # debug

def sendData(string):
    # convert input string to message payload
    destinationRouter = string.split(' ', 1)[0]
    start = (len(destinationRouter) + 1)
    end = 299 + start
    message = string[start:end]
    payload = 'DATA ' + config.routerName + ' ' + destinationRouter + ' ' + message
    try:
        adjacencyTable.acquire()
        packet = IP(dst=routingTable[destinationRouter])/UDP(sport=config.routerPort,dport=adjacencyTable[destinationRouter].port)/Raw(load=payload)
        send(packet, verbose=False)
        #packet.show() # debug
        adjacencyTable.release()
    except KeyError:
        print("{0}: Destination Unreachable".format(destinationRouter))
        adjacencyTable.release()
