import thread
from datetime import datetime

class Neighbor:
	def __init__(self, name, ipAddress):
		self.name = name
		self.ipAddress = ipAddress
		self.lastContact = datetime.utcnow()

	def updateLastContact(self):
		self.lastContact = datetime.utcnow()

class LinkState:
	def __init__(self, linkID, advRouter, seqNbr):
		self.linkID = linkID
		self.advRouter = advRouter
		self.seqNbr = seqNbr

	def getSeqNbr(self):
		return self.seqNbr

class NeighborsTable:
	def __init__(self):
		self.table = dict()
		self.lock = thread.allocate_lock()

	def insertNeighbor(self, routerName, ipAddress):
		self.table[routerName] = Neighbor(routerName, ipAddress)

	# returns true if routerName is present in the Neighbors Table, false otherwise
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



class LinkStateDatabase:
	def __init__(self):
		self.database = dict()
		self.lock = thread.allocate_lock()

	#def get(self, routerName):

	#NB: routerActiveLinks is a dictionary of class dict
	#def updateNeighbor(self, routerName, routerActiveLinks):

	#def updateNeighbor(self, routerName, routerActiveLinks):


# Global variables

neighborsTable = NeighborsTable()
linkStateDatabase = LinkStateDatabase()
