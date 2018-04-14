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
# Boucle de lancement
while True:
    s = input("Prompt>>")
    if s == 'show ip ospf neighbor':
        print(neighborsTable)
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
