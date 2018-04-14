# here is the principal file of sfp project
import sys
import threading
from data_structures import *
from packet_sender import *

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
adjacencyTable.insertAdjacency('RTR02', "192.168.1.3",3001)
print(adjacencyTable)


t1 = threading.Thread(target=gestionOfLSDU(config))
t1.start()

# Thread a lancer:
# - gestion de reception des packets
#packetReceiverThread = PacketReceiverThread()
#packetReceiverThread.start()
# - gestion d'envoi des LSDU
# - gestion d'envoi des HELLO
# - monitoring des LSUSent

# Boucle de lancement
while True:
    s = input("Prompt>>")
    if s == 'show running-config' or s == 'show run':
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
    elif s == 'exit':
        print("Goodbye !")
        exit()
    elif s[:3] == 'cmd':
        exec(s[4:])
    # more commands here...
    else:
        print(s)
        print("Error")
t1.join()
