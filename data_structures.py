import thread
from datetime import datetime

class Neighbor:
	def __init__(self, name, ipAddress, port, linkCost):
		self.name = name
		self.ipAddress = ipAddress
		self.port= port
		self.linkCost = linkCost

class Adjacency:
        def __init__(self, name, ipAddress):
                self.name = name
                self.ipAddress = ipAddress
                self.lastContact = datetime.utcnow()

        def updateLastContact(self):
                self.lastContact = datetime.utcnow()

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

# represents the list of neighbors as indicated by the configuration at launch
# NB: this table should not be edited during router operation, to insert new
# neighbors, refer to the adjacency table
class NeighborsTable:
        def __init__(self):
                self.table = dict()

        def insertNeighbor(self, routerName, ipAddress, port, linkCost):
                self.table[routerName] = Neighbor(routerName, ipAddress, port, linkCost)

        # returns true if routerName is present in the Adjacency Table, false otherwise
        def contains(self, routerName):
                try:
                        self.table[routerName]
                        return True
                except KeyError:
                        return False

        def __str__(self):
                toString = "###NEIGHBORS TABLE###\nNeighbor\tIP Address\t\tPort\tLink Cost\n"
                for key, value in self.table.items():
                        toString += key + "\t\t" + value.ipAddress + "\t\t" + value.port + "\t" + value.linkCost + "\n"
                return toString


class AdjacencyTable:
	def __init__(self):
		self.table = dict()
		self.lock = thread.allocate_lock()

	def insertAdjacency(self, routerName, ipAddress):
		self.table[routerName] = Adjacency(routerName, ipAddress)

	# returns true if routerName is present in the Adjacency Table, false otherwise
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
                        print("ERROR: could not update dead timer for {0} - neighbor is not present in table".format(routerName))

	def acquire(self):
		self.lock.acquire(True)

	def release(self):
		self.lock.release()

	def __str__(self):
		toString = "###ADJACENCY TABLE###\nNeighbor\tIP Address\t\tLast Contact\n"
		for key, value in self.table.items():
			toString += key + "\t\t" + value.ipAddress + "\t\t" + value.lastContact.strftime("%Y-%m-%d %H:%M:%S") + "\n"
		return toString



class LinkStateDatabase:
	def __init__(self):
		self.database = dict()
		self.lock = thread.allocate_lock()

	#NB: routerActiveLinks is a dictionary of class dict
	def insertEntries(self, routerName, routerActiveLinks, seqNbr):
		self.database[routerName] = LinkState(routerName, routerActiveLinks, seqNbr)

	def updateEntries(self, routerName, routerActiveLinks, seqNbr):
		try:
			self.database[routerName].updateActiveLinks(routerActiveLinks, seqNbr)
		except KeyError:
			print("ERROR: could not update neighbor {0} - neighbor is not present in database".format(routerName))

	# returns true if routerName is present in the Link State Database, false otherwise
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
			print("ERROR: {0} is not in database - sequence number requested".format(routerName))
			return 100

	def acquire(self):
		self.lock.acquire(True)

	def release(self):
		self.lock.release()

	def __str__(self):
		toString = "###LINK STATE DATABASE###\nAdvertising Router\tNeighboor\tLink Cost\n"
		for key, value in self.database.items():
			for subKey, subValue in value.activeLinks.items():
				toString += key + "\t\t\t" + subKey + "\t\t" + subValue + "\n"
		return toString


# Global variables

neighborsTable = NeighborsTable()
adjacencyTable = AdjacencyTable()
linkStateDatabase = LinkStateDatabase()
