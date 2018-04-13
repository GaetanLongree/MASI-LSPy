import _thread
import configparser
from datetime import datetime


class Config:
    maxLSPDelay = 0
    helloDelay = 0

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if config['CONFIG']['ROUTER_NAME'] == "":
            raise ValueError('config is not edited, please change it')

        self.routerName = config['CONFIG']['ROUTER_NAME']
        self.routerPort = config['CONFIG']['ROUTER_PORT']
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

    def __str__(self):
        toString = "###SERVER CONFIGURATION###\n"
        toString += "Router Name\t" + self.routerName + "\n"
        toString += "Router Port\t" + self.routerPort + "\n"
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

    def __init__(self, name, ipAddress):
        self.name = name
        self.ipAddress = ipAddress
        self.lastContact = datetime.utcnow()

    def updateLastContact(self):
        self.lastContact = datetime.utcnow()

    def __str__(self):
        toString = "Adjacency: " + self.name + "\n"
        toString += "IP Address\tLast Contact\n"
        toString += self.ipAddress + "\t" + self.lastContact.strftime("%Y-%m-%d %H:%M:%S") + "\n"
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
                "\t\t" + value.port + "\t" + value.linkCost + "\n"
        return toString


class AdjacencyTable:

    def __init__(self):
        self.table = dict()
        self.lock = _thread.allocate_lock()

    def insertAdjacency(self, routerName, ipAddress):
        self.table[routerName] = Adjacency(routerName, ipAddress)

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
        toString = "###ADJACENCY TABLE###\nNeighbor\tIP Address\t\tLast Contact\n"
        for key, value in self.table.items():
            toString += key + "\t\t" + value.ipAddress + "\t\t" + \
                value.lastContact.strftime("%Y-%m-%d %H:%M:%S") + "\n"
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
                toString += key + "\t\t\t" + subKey + "\t\t" + str(subValue) + "\n"
        return toString


# Global variables
config = None
neighborsTable = NeighborsTable()
adjacencyTable = AdjacencyTable()
linkStateDatabase = LinkStateDatabase()
