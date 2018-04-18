import _thread
import configparser
import ifaddr
from colored import *
from datetime import datetime


class RoutingTable(dict):

    def __init__(self, *args, **kw):
        super(RoutingTable, self).__init__(*args, **kw)
        self.lock = _thread.allocate_lock()

    def populateFromSPF(self, spfGraph):
        # print("Creating routing table from SPF") #debug
        # for each entry in the graph look at the previous node until == config.routerName
        # TODO at execution check if neighborsTable and adjacencyTable need
        # lock acquirement
        self.acquire()
        self.clear()
        for key, value in spfGraph.items():
            # print("Current key: " + key) #debug
            if value.previousNode is not None:
                nextHop = None
                tempHop = value.previousNode
                # print("Temp Hop: " + tempHop) #debug
                while tempHop != config.routerName:
                    nextHop = tempHop
                    tempHop = spfGraph[tempHop].previousNode
                    # print("Next Hop: " + nextHop) #debug
                    # print("Temp Hop: " + tempHop) #debug
                try:
                    if nextHop is not None:
                        self[key] = neighborsTable[nextHop].name
                    else:
                        self[key] = neighborsTable[key].name
                except KeyError:
                    try:
                        if nextHop is not None:
                            self[key] = adjacencyTable[nextHop].name
                        else:
                            self[key] = adjacencyTable[key].name
                    except KeyError:
                        if nextHop is not None:
                            print("{}ERROR: {} is neither Neighbors Table nor Adjacency Table - could not retrieve next hop IP{}".format(
                                fg('160'), nextHop, attr('reset')))
                        else:
                            print("{}ERROR: {} is neither Neighbors Table nor Adjacency Table - could not retrieve next hop IP{}".format(
                                fg('160'), key, attr('reset')))
        self.release()

    def acquire(self):
        self.lock.acquire(True)

    def release(self):
        self.lock.release()

    def __str__(self):
        toString = "%s###ROUTING TABLE###%s%s\nDestination\tNext Hop\n%s" % (
            fg('112'), attr('reset'), fg('14'), attr('reset'))
        for key, value in self.items():
            toString += key + "\t\t" + value + "\n"
        return toString

    def web(self):
        toString = "<h2>###ROUTING TABLE###</h2><table style='text-align:center;border-collapse:collapse;'>" \
            + "<tr><th style='padding-left:5px;padding-right:5px'>Destination</th><th style='padding-left:5px;padding-right:5px'>Next Hop</th></tr>"
        for key, value in self.items():
            toString += "<tr><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + key + \
                "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + \
                value + "</td></tr>"
        toString += "</table>"
        return toString


class LSUSent:

    def __init__(self, routerName, lspSourceName, sequenceNumber, payload, retransCounter):
        self.routerName = routerName
        self.lspSourceName = lspSourceName
        self.sequenceNumber = int(sequenceNumber)
        self.payload = payload
        self.retransCounter = retransCounter

    def __str__(self):
        toString = "LSUSent: " + self.routerName + "\n"
        toString += "LSP Source\tSequence Number\tPayload\tretransCounter\n"
        toString += self.lspSourceName + "\t" + self.sequenceNumber + "\t" + \
            self.payload + "\t" + str(self.retransCounter) + "\n"
        return toString


class LSUSentHandlerThreads(list):

    def __init__(self):
        list.__init__(self)
        self.lock = _thread.allocate_lock()

    def acquire(self):
        self.lock.acquire(True)

    def release(self):
        self.lock.release()


class LSUSentTable(list):

    def __init__(self):
        list.__init__(self)
        self.lock = _thread.allocate_lock()

    def insertLSUSent(self, routerName, lsuSourceName, sequenceNumber, payload):
        lsuSent = LSUSent(routerName, lsuSourceName,
                          sequenceNumber, payload, 0)
        self.append(lsuSent)
        return lsuSent

    # returns True if a matching LSUSent is present, False otherwise
    def contains(self, routerName, lspSourceName, seqNbr):
        for lsuSent in self:
            if lsuSent.routerName == routerName and lsuSent.lspSourceName == lspSourceName and lsuSent.sequenceNumber == int(seqNbr):
                return True
        return False

    # returns the index position of the LSUSent matching the given parameters,
    # None otherwise
    def getIndex(self, routerName, lspSourceName, seqNbr):
        for index in range(0, len(self)):
            if self[index].routerName == routerName and self[index].lspSourceName == lspSourceName and self[index].sequenceNumber == int(seqNbr):
                return index
        return None

    def updateRetransCounter(self, routerName, lspSourceName, seqNbr):
        index = self.contains(routerName, lspSourceName, seqNbr)
        if index is not None:
            self[index].retransCounter += 1
        else:
            print("{}ERROR: LSU to {} from {} is not in LSUSent table - retransmission counter not updated{}".format(fg('160'),
                                                                                                                     routerName, lspSourceName, attr('reset')))

    def deleteEntry(self, routerName, lspSourceName, seqNbr):
        index = self.getIndex(routerName, lspSourceName, seqNbr)
        if index is not None:
            self.pop(index)
        # Error message ignored because too many outputs
        # else:
        #    print("{}ERROR: LSU to {} from {} is not in LSUSent table - could not delete entry{}".format(fg('160'),
        # routerName, lspSourceName, attr('reset')))

    def acquire(self):
        self.lock.acquire(True)

    def release(self):
        self.lock.release()

    def __str__(self):
        toString = "%s###LSUSent TABLE###%s%s\nRouter Name\tLSP Source\tSeq Nbr\t\tRetrans. Counter\tPayload\n%s" % (
            fg('112'), attr('reset'), fg('14'), attr('reset'))
        for value in self:
            toString +=  "%s" % (fg('227')) + value.routerName  + "%s\t\t" % (attr('reset')) +  value.lspSourceName + "\t\t" + str(value.sequenceNumber) + \
                "\t\t" + str(value.retransCounter) + \
                "\t\t\t" + value.payload + "\n"
        return toString

    def web(self):
        toString = "<h2>###LSUSent TABLE###</2><table style='text-align:center;border-collapse:collapse;'>" \
            + "<tr><th style='padding-left:5px;padding-right:5px'>Router Name</th><th style='padding-left:5px;padding-right:5px'>LSP Source</th><th style='padding-left:5px;padding-right:5px'>Seq Nbr</th><th style='padding-left:5px;padding-right:5px'>Retrans. Counter</th><th style='padding-left:5px;padding-right:5px'>Payload"
        for value in self:
            toString +=  "<tr><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + value.routerName  + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" +  value.lspSourceName + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + str(value.sequenceNumber) + \
                "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + str(value.retransCounter) + \
                "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + \
                value.payload + "</td></tr>"
        toString += "</table>"
        return toString


class Config:

    def __init__(self):
        self.routerName = ''
        self.routerPort = 0
        self.maxLSPDelay = 0
        self.helloDelay = 0
        self.ipAddresses = []
        self.seqNbrInt = 0

    def readConfig(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if config['CONFIG']['ROUTER_NAME'] == "":
            raise ValueError('%sconfig is not edited, please change it%s' % (
                fg('160'), attr('reset')))

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

        # TODO move this to LSDU handler to update seqNbr for each new LSDU
        # generated
        activeLinks = dict()
        for key, value in neighborsTable.items():
            activeLinks[key] = value.linkCost
        linkStateDatabase.acquire()
        linkStateDatabase.insertEntries(self.routerName, activeLinks, 0)
        linkStateDatabase.release()

        # store all server's interface IP addresses
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            for ip in adapter.ips:
                self.ipAddresses.append(ip.ip)

    def __str__(self):
        toString = "%s###SERVER CONFIGURATION###\n%s" % (
            fg('112'), attr('reset'))
        toString += "%sRouter Name\t%s" % (fg('227'),
                                           attr('reset')) + self.routerName + "\n"
        toString += "%sRouter Port\t%s" % (fg('227'),
                                           attr('reset')) + str(self.routerPort) + "\n"
        toString += "%sHello Delay\t%s" % (fg('227'),
                                           attr('reset')) + str(self.helloDelay) + "\n"
        toString += "%sMax LSP Delay\t%s" % (fg('227'),
                                             attr('reset')) + str(self.maxLSPDelay) + "\n\n"
        toString += "%sNeighbors configured in config.ini file:%s\n" % (
            fg('orange_red_1'), attr('reset'))
        toString += neighborsTable.__str__()
        return toString

    def web(self):
        toString = "<h1>" + config.routerName + "</h1>"
        toString += "<h2>###SERVER CONFIGURATION###</h2><table style='text-align:center;border-collapse:collapse;'>"
        toString += "<tr><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>Router Name</td>"
        toString += "<td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>Router Port</td>"
        toString += "<td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>Hello Delay</td>"
        toString += "<td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>Max LSP Delay</td></tr>"
        toString += "<tr><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + self.routerName + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + \
            str(self.routerPort) + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + str(self.helloDelay) + \
            "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + \
            str(self.maxLSPDelay) + "</td></tr>"
        toString += "</table><h3>Neighbors configured in config.ini file</h3>"
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


class NeighborsTable(dict):

    def __init__(self, *args, **kw):
        super(NeighborsTable, self).__init__(*args, **kw)

    def insertNeighbor(self, routerName, ipAddress, port, linkCost):
        self[routerName] = Neighbor(routerName, ipAddress, port, linkCost)

    # returns true if routerName is present in the Adjacency Table, false
    # otherwise
    def contains(self, routerName):
        try:
            self[routerName]
            return True
        except KeyError:
            return False

    def __str__(self):
        toString = "%s###NEIGHBORS TABLE###%s%s\nNeighbor\tIP Address\t\tPort\tLink Cost\n%s" % (
            fg('112'), attr('reset'), fg('14'), attr('reset'))
        for key, value in self.items():
            toString += "%s" % (fg('227')) + key + "%s\t\t" % (attr('reset')) + value.ipAddress + \
                "\t\t" + str(value.port) + "\t" + str(value.linkCost) + "\n"
        return toString

    def web(self):
        toString = "<h2>###NEIGHBORS TABLE###</h2><table style='text-align:center;border-collapse:collapse;'>" \
            + "<tr><th style='padding-left:5px;padding-right:5px'>Neighbor</th><th style='padding-left:5px;padding-right:5px'>IP Address</th><th style='padding-left:5px;padding-right:5px'>Port</th><th style='padding-left:5px;padding-right:5px'>Link Cost</th></tr>"
        for key, value in self.items():
            toString += "<tr><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + key + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + value.ipAddress + \
                "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + str(value.port) + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + \
                str(value.linkCost) + "</td></tr>"
        toString += "</table>"
        return toString


class AdjacencyTable(dict):

    def __init__(self, *args, **kw):
        super(AdjacencyTable, self).__init__(*args, **kw)
        self.lock = _thread.allocate_lock()

    def insertAdjacency(self, routerName, ipAddress, port):
        self[routerName] = Adjacency(routerName, ipAddress, port)

    # returns true if routerName is present in the Adjacency Table, false
    # otherwise
    def contains(self, routerName):
        try:
            self[routerName]
            return True
        except KeyError:
            return False

    def updateDeadTimer(self, routerName):
        try:
            self[routerName].updateLastContact()
        except KeyError:
            print(
                "{}ERROR: could not update dead timer for {} - neighbor is not present in table{}".format(fg('160'), routerName, attr('reset')))

    def remove(self, key):
        try:
            print("No Hello received from " +
                  self[key].name + " for more than 4 * Hello Delay - removing from adjacency...")
            self.pop(key)
        except KeyError:
            print("{}ERROR: could not remove {} from adjacency table - neighbor is not present{}".format(
                fg('160'), key, attr('reset')))

    def acquire(self):
        self.lock.acquire(True)

    def release(self):
        self.lock.release()

    def __str__(self):
        toString = "%s###ADJACENCY TABLE###%s%s\nNeighbor\tIP Address\t\tPort\tLast Contact\n%s" % (
            fg('112'), attr('reset'), fg('14'), attr('reset'))
        for key, value in self.items():
            toString +=  "%s" % (fg('227')) + key + "%s\t\t" % (attr('reset')) + value.ipAddress + "\t\t" + \
                str(value.port) + "\t" + \
                value.lastContact.strftime("%Y-%m-%d %H:%M:%S") + "\n"
        return toString

    def web(self):
        toString = "<h2>###ADJACENCY TABLE###</h2> <table style='text-align:center;border-collapse:collapse;'>" \
            + "<tr><th style='padding-left:5px;padding-right:5px'>Neighbor</th><th style='padding-left:5px;padding-right:5px'>IP</th><th style='padding-left:5px;padding-right:5px'>Address</th><th style='padding-left:5px;padding-right:5px'>Port</th><th style='padding-left:5px;padding-right:5px'>Last Contact</th> </tr>"
        for key, value in self.items():
            toString +=  "<tr><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + key + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + value.ipAddress + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + \
                str(value.port) + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + \
                value.lastContact.strftime("%Y-%m-%d %H:%M:%S") + "</td></tr>"
        toString += "</table>"
        return toString


class LinkStateDatabase(dict):

    def __init__(self, *args, **kw):
        super(LinkStateDatabase, self).__init__(*args, **kw)
        self.lock = _thread.allocate_lock()

    # NB: routerActiveLinks is a dictionary of class dict
    def insertEntries(self, routerName, routerActiveLinks, seqNbr):
        self[routerName] = LinkState(routerName, routerActiveLinks, seqNbr)

    def updateEntries(self, routerName, routerActiveLinks, seqNbr):
        try:
            self[routerName].updateActiveLinks(routerActiveLinks, seqNbr)
        except KeyError:
            print(
                "{}ERROR: could not update neighbor {} - neighbor is not present in database{}".format(fg('160'), routerName, attr('reset')))

    # returns true if routerName is present in the Link State Database, false
    # otherwise
    def contains(self, routerName):
        try:
            self[routerName]
            return True
        except KeyError:
            return False

    def getSeqNumber(self, routerName):
        try:
            return self[routerName].seqNbr
        except KeyError:
            # should not happen, returns number higher than max seq number to avoid updating
            # non existant entry
            print(
                "{}ERROR: {} is not in database - sequence number requested{}".format(fg('160'), routerName, attr('reset')))
            return 100

    def removeEntries(self, key):
        try:
            del self[key]
            self[config.routerName].activeLinks.pop(key)
        except KeyError:
            print(
                "{}ERROR: could not remove {} from link state database - router is not present{}".format(fg('160'), key, attr('reset')))

    def acquire(self):
        self.lock.acquire(True)

    def release(self):
        self.lock.release()

    def __str__(self):
        toString = "%s###LINK STATE DATABASE###%s%s\nAdvertising Router\tNeighboor\tLink Cost\n%s" % (
            fg('112'), attr('reset'), fg('14'), attr('reset'))
        for key, value in self.items():
            for subKey, subValue in value.activeLinks.items():
                toString +=  "%s" % (fg('227')) + key + "%s\t\t" % (attr('reset')) + subKey + \
                    "\t\t" + str(subValue) + "\n"
        return toString

    def web(self):
        toString = "<h2>###LINK STATE DATABASE###</h2><table style='text-align:center;border-collapse:collapse;'>" \
            + "<tr><th style='padding-left:5px;padding-right:5px'>Advertising Router</th><th style='padding-left:5px;padding-right:5px'>Neighboor</th><th style='padding-left:5px;padding-right:5px'>Link Cost</th></tr>"
        for key, value in self.items():
            for subKey, subValue in value.activeLinks.items():
                toString +=  "<tr><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + key + "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + subKey + \
                    "</td><td style='padding-left:5px;padding-right:5px;border:solid 1px black;'>" + \
                    str(subValue) + "</td></tr>"
        toString += "</table>"
        return toString

# Global variables
config = Config()
routingTable = RoutingTable()
lSUSentTable = LSUSentTable()
neighborsTable = NeighborsTable()
adjacencyTable = AdjacencyTable()
linkStateDatabase = LinkStateDatabase()
lsuSentHandlerThreads = LSUSentHandlerThreads()
