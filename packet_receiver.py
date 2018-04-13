# TODO manage LSACK 

from scapy.all import *
#from packet_sender import *
from data_structures import *
import threading

class PacketReceiverThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.threadNOTRunning = False

	def helloPacketHandler(self, pkt, pktArray):
		#[0]HELLO [1]Sender Name [2]Receiver Name
		if pktArray[2] == config.routerName:
			print("Received a HELLO packet from {0}".format(pktArray[2]))
			if adjacencyTable.contains(pktArray[1]):
				adjacencyTable.acquire()
				adjacencyTable.updateDeadTimer(pktArray[1])
				adjacencyTable.release()
			else:
				adjacencyTable.acquire()
				adjacencyTable.insertAdjacency(pktArray[1], pkt[IP].src)
				adjacencyTable.release()
		#print(adjacencyTable)	# debug

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

		if adjacencyTable.contains(pktArray[1]):
			# Convert Adjacent Active Links pair in 2 dimension table lsdUpdate[Neighbor][LinkCost]
			activeLinks = self.activeLinkPairsHandler(pktArray)
			if linkStateDatabase.contains(pktArray[1]):
				if pktArray[2] > linkStateDatabase.getSeqNumber(pktArray[1]):
					# Update existing entries in the LSDB
					linkStateDatabase.acquire()
					linkStateDatabase.updateEntries(pktArray[1], activeLinks, pktArray[2])
					linkStateDatabase.release()
					# forward received LSDU to all other neighbors
			else:
				# Insert new entries in the LSDB
				linkStateDatabase.acquire()
				linkStateDatabase.insertEntries(pktArray[1], activeLinks, pktArray[2])
				linkStateDatabase.release()
				# forward received LSDU to all other neighbors
			# send LSACK to sender
			# launch SPF recalculation
		#print(linkStateDatabase)	# debug

	def packetTreatment(self, pkt):
		pktArray = ((pkt[Raw].load).decode("utf-8")).split()
		#print(pktArray) # debug
		if pktArray[0] == "HELLO":
			self.helloPacketHandler(pkt, pktArray)
		if pktArray[0] == "LSP":
			self.lspPacketHandler(pkt, pktArray)

	def packetCallback(self, pkt):
		if UDP in pkt:
			if pkt[UDP].dport == config.routerPort:
				#pkt.show() # debug
				self.packetTreatment(pkt)
	def run(self):
		# launch packet sniffing continuously, listening to any received packets
		sniff(prn=self.packetCallback, store=0, stop_filter=self.threadNOTRunning)

	def stop(self):
		self.threadNOTRunning = True
		print("Thread NOT Running : {0}".format(self.threadNOTRunning))
