# TODO update run() with a method to stop it from parent
# TODO manage LSACK 
# TODO check if sniff overrides Linux reception

from scapy.all import *
#from server import ROUTER_NAME, ROUTER_PORT
#from lsp_update import sendLSDUpdate
from data_structures import *
import threading

ROUTER_NAME = "RTR-01"
ROUTER_PORT = 30000

class PacketReceiverThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.threadNOTRunning = False

	def helloPacketHandler(self, pkt, pktArray):
		#[0]HELLO [1]Sender Name [2]Receiver Name
		if pktArray[2] == ROUTER_NAME:
			print("Received a HELLO packet from {0}".format(pktArray[2]))
			if neighborsTable.contains(pktArray[1]):
				neighborsTable.acquire()
				neighborsTable.updateDeadTimer(pktArray[1])
				neighborsTable.release()
			else:
				neighborsTable.acquire()
				neighborsTable.insertNeighbor(pktArray[1], pkt[IP].src)
				neighborsTable.release()
		#print(neighborsTable)	# debug

	def activeLinkPairsHandler(self, pktArray):
		activeLinks = dict()
		i = 3
		while (i < len(pktArray)):
			activeLinks[pktArray[i]] = pktArray[i+1]
			i = i+2
		return activeLinks

	def lspPacketHandler(self, pkt, pktArray):
		# [0]LSP [1]Sender Name [2]Sequence Number [3..N]Adjacent Active Links in pairs [Neighbor Name, Link Cost]
		# [3]Neighbor 1 Name [4]Link Cost to Neighbor 1 [5]Neighbor 2 Name [6]Link Cost to Neighbor 2 [...]
		print("Received a LSP packet from {0}".format(pktArray[1]))

		if neighborsTable.contains(pktArray[1]):
			# Convert Adjacent Active Links pair in 2 dimension table lsdUpdate[Neighbor][LinkCost]
			activeLinks = self.activeLinkPairsHandler(pktArray)
			if linkStateDatabase.contains(pktArray[1]):
				if pktArray[2] > linkStateDatabase.getSeqNumber(pktArray[1]):
					# Update existing entries in the LSDB
					linkStateDatabase.acquire()
					linkStateDatabase.updateEntries(pktArray[1], activeLinks, pktArray[2])
					linkStateDatabase.release()
			else:
				# Insert new entries in the LSDB
				linkStateDatabase.acquire()
				linkStateDatabase.insertEntries(pktArray[1], activeLinks, pktArray[2])
				linkStateDatabase.release()
			# send LSACK to sender
			# forward received LSDU to all other neighbors
			# launch SPF recalculation
		#print(linkStateDatabase)	# debug

	def packetTreatment(self, pkt):
		pktArray = (pkt[Raw].load).split()
		if pktArray[0] == "HELLO":
			self.helloPacketHandler(pkt, pktArray)
		if pktArray[0] == "LSP":
			self.lspPacketHandler(pkt, pktArray)

	def packetCallback(self, pkt):
		if UDP in pkt:
			if pkt[UDP].dport == ROUTER_PORT:
				#print(pkt[Raw].load) # debug statement
				self.packetTreatment(pkt)
	def run(self):
		while self.threadRunning == True:
			# launch packet sniffing continuously, listening to any received packets
			sniff(prn=self.packetCallback, store=0, stop_filter=self.threadNOTRunning)

	def stop(self):
		self.threadNOTRunning = True
