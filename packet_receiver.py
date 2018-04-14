from scapy.all import *
from packet_sender import sendLSAck
from data_structures import *
from spf_algorithm import *
import threading

class PacketReceiverThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.threadNOTRunning = False

	def helloPacketHandler(self, pkt, pktArray):
		#[0]HELLO [1]Sender Name [2]Receiver Name
		if pktArray[2] == config.routerName:
			print("Received a HELLO packet from {0}".format(pktArray[1]))
			if adjacencyTable.contains(pktArray[1]):
				adjacencyTable.acquire()
				adjacencyTable.updateDeadTimer(pktArray[1])
				adjacencyTable.release()
			else:
				adjacencyTable.acquire()
				adjacencyTable.insertAdjacency(pktArray[1], pkt[IP].src, pkt[UDP].sport)
				adjacencyTable.release()
		#print(adjacencyTable)	# debug

	def activeLinkPairsHandler(self, pktArray):
		try:
			activeLinks = dict()
			i = 3
			while (i < len(pktArray)):
				activeLinks[pktArray[i]] = pktArray[i+1]
				i = i+2
			return activeLinks
		except IndexError:
			print("ERROR: bad LSP format received from {0} - ignoring update".format(pktArray[1]))
			return None

	def lspPacketHandler(self, pkt, pktArray):
		# [0]LSP [1]Sender Name [2]Sequence Number [3..N]Adjacent Active Links in pairs [Neighbor Name, Link Cost]
		# [3]Neighbor 1 Name [4]Link Cost to Neighbor 1 [5]Neighbor 2 Name [6]Link Cost to Neighbor 2 [...]
		if pktArray[1] != config.routerName:
			print("Received a LSP packet from {0}".format(pktArray[1]))

			if adjacencyTable.contains(pktArray[1]):
				# Convert Adjacent Active Links pair in 2 dimension table lsdUpdate[Neighbor][LinkCost]
				activeLinks = self.activeLinkPairsHandler(pktArray)
				if activeLinks != None:
					if linkStateDatabase.contains(pktArray[1]):
						if pktArray[2] > linkStateDatabase.getSeqNumber(pktArray[1]):
							# Update existing entries in the LSDB
							linkStateDatabase.acquire()
							linkStateDatabase.updateEntries(pktArray[1], activeLinks, pktArray[2])
							linkStateDatabase.release()
							# TODO forward received LSDU to all other neighbors
					else:
						# Insert new entries in the LSDB
						linkStateDatabase.acquire()
						linkStateDatabase.insertEntries(pktArray[1], activeLinks, pktArray[2])
						linkStateDatabase.release()
						# TODO forward received LSDU to all other neighbors
					# send LSACK to sender
					sendLSAck(pkt[IP].src, pkt[UDP].sport, pktArray[1], pktArray[2])
					# launch SPF recalculation
					spf.run()
			#print(linkStateDatabase)	# debug


	def lsackPacketHandler(self, pkt, pktArray):
		# [0]LSACK [1]ACK Source Name [2]LSP Sender Name [3]Sequence Number
		if pktArray[1] != config.routerName:
			print("Received a LSACK packet from {0}".format(pktArray[1]))

			if lSUSentTable.contains(pktArray[1], pktArray[2], pktArray[3]):
				lSUSentTable.acquire()
				lSUSentTable.deleteEntry(pktArray[1], pktArray[2], pktArray[3])
				lSUSentTable.release()
	                #print(lSUSentTable)       # debug

	def dataPacketHandler(self, pkt, pktArray):
		# [0]DATA [1]Sender Name [2]Destination Name [3...]Message
		if pktArray[1] != config.routerName and pkt[IP].src not in config.ipAddresses:
			if pktArray[2] == config.routerName:
				print("Received a message from {0}:".format(pktArray[1]))
				start = (len(pktArray[0]) + len(pktArray [1]) + len(pktArray[2]) + 3)
				end = 299 + start
				print((pkt[Raw].load).decode("utf-8")[start:end])
			else:
				print("Received message from {0} for {1} - routing packet".format(pktArray[1], pktArray[2]))
				try:
					send(IP(dst=routingTable[pktArray[2]])/UDP(sport=config.routerPort,dport=adjacencyTable.table[pktArray[2]].port)/Raw(load=(pkt[Raw].load).decode("utf-8")))
				except KeyError:
					print("{0}: Destination Unreachable".format(pktArray[2]))

	def packetTreatment(self, pkt):
		pktArray = ((pkt[Raw].load).decode("utf-8")).split()
		#print(pktArray) # debug
		if pktArray[0] == "HELLO":
			self.helloPacketHandler(pkt, pktArray)
		if pktArray[0] == "LSP":
			self.lspPacketHandler(pkt, pktArray)
		if pktArray[0] == "LSACK":
                        self.lsackPacketHandler(pkt, pktArray)
		if pktArray[0] == "DATA":
			self.dataPacketHandler(pkt, pktArray)

	def packetCallback(self, pkt):
		global config
		if UDP in pkt:
			if pkt[UDP].dport == config.routerPort:
				#pkt.show() # debug
				self.packetTreatment(pkt)
	def run(self):
		# launch packet sniffing continuously, listening to any received packets
		sniff(prn=self.packetCallback, store=0, stop_filter=self.threadNOTRunning)

	def stop(self):
		self.threadNOTRunning = True
		#print("Thread NOT Running : {0}".format(self.threadNOTRunning)) # debug
