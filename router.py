# here is the principal file of sfp project
# dependecies : scapy , colored, ifappdr
import sys
import threading
from colored import *
from data_structures import *
from packet_receiver import *
from packet_sender import *
from adjacency_monitor import *
from webserv import *

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

webServThread = WebServThread()
webServThread.start()

time.sleep(1)
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
    elif s == 'show lsack queue':
        print(lSUSentTable)
    elif s[:4] == 'send':
        sendData(s[5:])
    elif s == 'help':
        print('%sTo send data:%s\n\tsend [destination] [message]\n\n' % (fg('14'), attr('reset')) +
              '%sAvailable commands:%s\n\tshow config / show running-config\n\t' % (fg('14'), attr('reset')) +
              'show neighbors / show ip ospf neighbor\n\tshow adjacency / show ip ospf adjacency\n\t' +
              'show database / show linkStateDatabase / show ip ospf database\n\tshow spf / show ip ospf\n\t' +
              'show route / show ip route\n\tshow lsack queue\n\tcmd [python-command]\n\n' +
              '%sTo quit the program:%s\n\texit\n' % (fg('14'), attr('reset')))
    elif s == 'exit':
        print("%sGoodbye !%s" % (fg('112'), attr('reset')))
        # stopping threads
        # debug
        print("Please wait for program to close correctly (may take a few seconds)")
        packetReceiverThread.stop()
        # print("packetReceiverThread stopped") # debug
        lsuHandlerThread.stop()
        # print("lsuHandlerThread stopped") # debug
        helloHandlerThread.stop()
        # print("helloHandlerThread stopped") # debug
        adjacencyMonitorThread.stop()
        # print("adjacencyMonitorThread stopped") # debug
        if adjacencyTable.lock.locked() == True:
            adjacencyTable.release()
        exit()
    elif s[:3] == 'cmd':
        try:
            exec(s[4:])
        except:
            print("%s" %
                  (fg('160') + str(sys.exc_info()[1]) + "%s" % attr('reset')))
        # more commands here...
    else:
        print(s)
        print("%sERROR: unknown command - enter 'help' for more info %s" %
              (fg('160'), attr('reset')))
