import _thread
import configparser
import ifaddr
from datetime import datetime

class RoutingTable(dict):
    def populateFromSPF(self, spfGraph):
        #print("Creating routing table from SPF") #debug
        # for each entry in the graph look at the previous node until == config.routerName
        for key, value in spfGraph.items():
            #print("Current key: " + key) #debug
            if value.previousNode is not None:
                nextHop = None
                tempHop = value.previousNode
                #print("Temp Hop: " + tempHop) #debug
                while tempHop != config.routerName:
                    nextHop = tempHop
                    tempHop = spfGraph[tempHop].previousNode
                    #print("Next Hop: " + nextHop) #debug
                    #print("Temp Hop: " + tempHop) #debug
                try:
                    if nextHop is not None:
                        self[key] = neighborsTable.table[nextHop].ipAddress
                    else:
                        self[key] = neighborsTable.table[key].ipAddress
                except KeyError:
                    try:
                        if nextHop is not None:
                            self[key] = adjacencyTable.table[nextHop].ipAddress
                        else:
                            self[key] = adjacencyTable.table[key].ipAddress
                    except KeyError:
                        if nextHop is not None:
                            print("ERROR: {0} is neither Neighbors Table nor Adjacency Table - could not retrieve next hop IP".format(nextHop))
                        else:
                            print("ERROR: {0} is neither Neighbors Table nor Adjacency Table - could not retrieve next hop IP".format(key))

    def __str__(self):
        toString = "###ROUTING TABLE###\nDestination\tNext Hop\n"
        for key, value in self.items():
            toString += key + "\t\t" + value + "\n"
        return toString


class LSUSent:

    def __init__(self, routerName, sequenceNumber, payload, retransCounter):
        self.routerName = routerName
        self.sequenceNumber = sequenceNumber
        self.payload = payload
        self.retransCounter = retransCounter

    def __str__(self):
        toString = "LSUSent: " + self.routerName + "\n"
        toString += "Sequence Number\tPayload\tretransCounter\n"
        toString += self.sequenceNumber + "\t" + \
            self.payload + "\t" + self.retransCounter + "\n"
        return toString


class LSUSentTable:

    def __init__(self):
        self.table = dict()
        self.lock = _thread.allocate_lock()

    def insertLSUSent(self, routerName, sequenceNumber, payload):
        self.table[routerName] = LSUSent(
            routerName, sequenceNumber, payload, 0)

    # returns true if routerName is present in the Adjacency Table, false
    # otherwise
    def contains(self, routerName):
        try:
            self.table[routerName]
            return True
        except KeyError:
            return False

    def updateRetransCounter(self, routerName):
        try:
            self.table[routerName].retransCounter += 1
        except KeyError:
            print("ERROR: {0} is not in LSUSent table - retransmission counter not updated".format(routerName))

    def deleteEntry(self, routerName, seqNbr):
        try:
            if self.table[routerName].sequenceNumber == seqNbr:
                del self.table[routerName]
        except KeyError:
            print("ERROR: {0} is not in LSUSent table - could not delete entry".format(routerName))

    def acquire(self):
        self.lock.acquire(True)

    def release(self):
        self.lock.release()

    def __str__(self):
        toString = "###LSUSent TABLE###\nRouter Name\tSeq Nbr\t\tRetrans. Counter\tPayload\n"
        for key, value in self.table.items():
            toString += key + "\t\t" + str(value.sequenceNumber) + \
                "\t\t" + str(value.retransCounter) + "\t\t\t" + value.payload + "\n"
        return toString


class Config:

    def __init__(self):
        self.routerName = ''
        self.routerPort = 0
        self.maxLSPDelay = 0
        self.helloDelay = 0
        self.ipAddresses = []

    def readConfig(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if config['CONFIG']['ROUTER_NAME'] == "":
            raise ValueError('config is not edited, please change it')

        self.routerName = config['CONFIG']['ROUTER_NAME']
        self.routerPort = int(config['CONFIG']['ROUTER_PORT'])
        flag = True
        nb_neig = 1
        while flag:
            name = "NEIGHBOR_" + str(nb_neig)
            try:
                test = config['CONFIG'][name]
                x = test.split(" ")
                neighborsTable.insertNeighbor(x[0], x[1], x[2], x[3])
                nb_neig += 1
            except KeyError:
                flag = False

        # TODO move this to LSDU handler to update seqNbr for each new LSDU generated
        activeLinks = dict()
        for key, value in neighborsTable.table.items():
            activeLinks[key] = value.linkCost
        linkStateDatabase.insertEntries(self.routerName, activeLinks, 0)

        #store all server's interface IP addresses
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            for ip in adapter.ips:
                self.ipAddresses.append(ip.ip)

    def __str__(self):
        toString = "###SERVER CONFIGURATION###\n"
        toString += "Router Name\t" + self.routerName + "\n"
        toString += "Router Port\t" + str(self.routerPort) + "\n"
        toString += "Hello Delay\t" + str(self.helloDelay) + "\n"
        toString += "Max LSP Delay\t" + str(self.maxLSPDelay) + "\n\n"
        toString += "Neighbors configured in config.ini file:\n"
        toString += neighborsTable.__str__()
        return toString


class Neighbor:

    def __init__(self, name, ipAddress, port, linkCost):
        self.name = name
        self.ipAddress = ipAddress
        self.port = port
        self.linkCost = linkCost

    def __str__(self):
        toString = "Neighbor: " + self.name + "\n"
        toString += "IP Address\tPort\tLink Cost\n"
        toString += self.ipAddress + "\t" + self.port + "\t" + self.linkCost + "\n"
        return toString


class Adjacency:

    def __init__(self, name, ipAddress, port):
        self.name = name
        self.ipAddress = ipAddress
        self.lastContact = datetime.utcnow()
        self.port = port

    def updateLastContact(self):
        self.lastContact = datetime.utcnow()

    def __str__(self):
        toString = "Adjacency: " + self.name + "\n"
        toString += "IP Address\tPort\tLast Contact\n"
        toString += self.ipAddress + "\t" + str(self.port) + "\t" + \
            self.lastContact.strftime("%Y-%m-%d %H:%M:%S") + "\n"
        return toString


class LinkState:

    def __init__(self, advRouter, activeLinks, seqNbr):
        self.advRouter = advRouter
        self.activeLinks = activeLinks
        self.seqNbr = seqNbr

    def getSeqNbr(self):
        return self.seqNbr

    def updateActiveLinks(self, newActiveLinks, seqNbr):
        self.activeLinks = newActiveLinks
        self.seqNbr = seqNbr

    def __str__(self):
        toString = "Link State: " + self.advRouter + "\n"
        toString += "Neighbor\tLink Cost\n"
        for key, value in self.activeLinks.items():
            toString += key + "\t\t" + str(value) + "\n"
        return toString

# represents the list of neighbors as indicated by the configuration at launch
# NB: this table should not be edited during router operation, to insert new
# neighbors, refer to the adjacency table


class NeighborsTable:

    def __init__(self):
        self.table = dict()

    def insertNeighbor(self, routerName, ipAddress, port, linkCost):
        self.table[routerName] = Neighbor(
            routerName, ipAddress, port, linkCost)

    # returns true if routerName is present in the Adjacency Table, false
    # otherwise
    def contains(self, routerName):
        try:
            self.table[routerName]
            return True
        except KeyError:
            return False

    def __str__(self):
        toString = "###NEIGHBORS TABLE###\nNeighbor\tIP Address\t\tPort\tLink Cost\n"
        for key, value in self.table.items():
            toString += key + "\t\t" + value.ipAddress + \
                "\t\t" + str(value.port) + "\t" + value.linkCost + "\n"
        return toString


class AdjacencyTable:

    def __init__(self):
        self.table = dict()
        self.lock = _thread.allocate_lock()

    def insertAdjacency(self, routerName, ipAddress, port):
        self.table[routerName] = Adjacency(routerName, ipAddress, port)

    # returns true if routerName is present in the Adjacency Table, false
    # otherwise
    def contains(self, routerName):
        try:
            self.table[routerName]
            return True
        except KeyError:
            return False

    def updateDeadTimer(self, routerName):
        try:
            self.table[routerName].updateLastContact()
        except KeyError:
            print(
                "ERROR: could not update dead timer for {0} - neighbor is not present in table".format(routerName))

    def acquire(self):
        self.lock.acquire(True)

    def release(self):
        self.lock.release()

    def __str__(self):
        toString = "###ADJACENCY TABLE###\nNeighbor\tIP Address\t\tPort\tLast Contact\n"
        for key, value in self.table.items():
            toString += key + "\t\t" + value.ipAddress + "\t\t" + str(value.port) + "\t" + value.lastContact.strftime("%Y-%m-%d %H:%M:%S") + "\n"
        return toString


class LinkStateDatabase:

    def __init__(self):
        self.database = dict()
        self.lock = _thread.allocate_lock()

    # NB: routerActiveLinks is a dictionary of class dict
    def insertEntries(self, routerName, routerActiveLinks, seqNbr):
        self.database[routerName] = LinkState(
            routerName, routerActiveLinks, seqNbr)

    def updateEntries(self, routerName, routerActiveLinks, seqNbr):
        try:
            self.database[routerName].updateActiveLinks(
                routerActiveLinks, seqNbr)
        except KeyError:
            print(
                "ERROR: could not update neighbor {0} - neighbor is not present in database".format(routerName))

    # returns true if routerName is present in the Link State Database, false
    # otherwise
    def contains(self, routerName):
        try:
            self.database[routerName]
            return True
        except KeyError:
            return False

    def getSeqNumber(self, routerName):
        try:
            return self.database[routerName].seqNbr
        except KeyError:
            # should not happen, returns number higher than max seq number to avoid updating
            # non existant entry
            print(
                "ERROR: {0} is not in database - sequence number requested".format(routerName))
            return 100

    def acquire(self):
        self.lock.acquire(True)

    def release(self):
        self.lock.release()

    def __str__(self):
        toString = "###LINK STATE DATABASE###\nAdvertising Router\tNeighboor\tLink Cost\n"
        for key, value in self.database.items():
            for subKey, subValue in value.activeLinks.items():
                toString += key + "\t\t\t" + subKey + \
                    "\t\t" + str(subValue) + "\n"
        return toString


# Global variables
config = Config()
routingTable = RoutingTable()
lSUSentTable = LSUSentTable()
neighborsTable = NeighborsTable()
adjacencyTable = AdjacencyTable()
linkStateDatabase = LinkStateDatabase()
