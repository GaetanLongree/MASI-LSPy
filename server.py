# here is the principal file of sfp project
import sys
import threading
from data_structures import *
from packet_receiver import *
from packet_sender import *
from adjacency_monitor import *

config.readConfig()

if(len(sys.argv) <= 1):
    print("programme sans arguments")
    config.helloDelay = 5
    config.maxLSPDelay = 60
else:
    print("programme avec arguments")
    config.helloDelay = sys.argv[1]
    config.maxLSPDelay = sys.argv[2]

print(config)

# thread toute les 5 secondes verifier lsusent
# un pour envoyé les lsu



# Thread a lancer:
# - gestion de reception des packets
packetReceiverThread = PacketReceiverThread()
packetReceiverThread.start()
# - gestion d'envoi des LSDU
lsuHandlerThread = LSUHandlerThread()
lsuHandlerThread.start()
# - gestion d'envoi des HELLO
helloHandlerThread = HelloHandlerThread()
helloHandlerThread.start()
# - monitoring des Adjacency
adjacencyMonitorThread = AdjacencyMonitorThread()
adjacencyMonitorThread.start()

# Boucle de lancement
while True:
    s = input(config.routerName + "#")
    if s == 'show running-config' or s == 'show config':
        print(config)
    elif s == 'show ip ospf neighbor' or s == 'show neighbors':
        print(neighborsTable)
    elif s == 'show ip ospf adjacency' or s == 'show adjacency':
        print(adjacencyTable)
    elif s == 'show ip ospf database' or s == 'show database' or s == 'show linkStateDatabase':
        print(linkStateDatabase)
    elif s == 'show ip ospf' or s == 'show spf':
        print(spf)
    elif s == 'show ip route' or s == 'show route':
        print(routingTable)
    elif s[:4] == 'send':
        sendData(s[5:])
    elif s == 'help':
        print('To send data:\n\tsend [destination] [message]\n\nAvailable commands:\n\tshow config / show running-config\n\tshow neighbors / show ip ospf neighbor\n\tshow adjacency / show ip ospf adjacency\n\tshow database / show linkStateDatabase / show ip ospf database\n\tshow spf / show ip ospf\n\tshow route / show ip route\n\tcmd [python-command]\n\nTo quit the program:\n\texit\n')
    elif s == 'exit':
        print("Goodbye !")
        #stopping threads
        print("Please wait for program to close correctly (may take a few seconds)") # debug
        packetReceiverThread.stop()
        #print("packetReceiverThread stopped") # debug
        lsuHandlerThread.stop()
        #print("lsuHandlerThread stopped") # debug
        helloHandlerThread.stop()
        #print("helloHandlerThread stopped") # debug
        adjacencyMonitorThread.stop()
        #print("adjacencyMonitorThread stopped") # debug
        if adjacencyTable.lock.locked() == True:
            adjacencyTable.release()
        exit()
    elif s[:3] == 'cmd':
        exec(s[4:])
    # more commands here...
    else:
        print(s)
        print("ERROR: unknown command - enter 'help' for more info")
