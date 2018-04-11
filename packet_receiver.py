from scapy.all import *
#from server import ROUTER_NAME, ROUTER_PORT
#from lsp_update import sendLSDUpdate
from data_structures import *

ROUTER_NAME = "RTR-01"
ROUTER_PORT = 30000

def helloPacketHandler(pkt, pktArray):
	#[0]HELLO [1]Sender Name [2]Receiver Name
	if pktArray[2] == ROUTER_NAME:
		print("Received a HELLO packet from {0}".format(pktArray[2]))
		if neighborsTable.contains(pktArray[1]):
			neighborsTable.updateDeadTimer(pktArray[1])
		else:
			neighborsTable.insertNeighbor(pktArray[1], pkt[IP].src)
	print(neighborsTable)	# debug

def activeLinkPairsHandler(pktArray):
	activeLinks = dict()
	i = 3
	while (i < len(pktArray)):
		activeLinks[pktArray[i]] = pktArray[i+1]
		i = i+2
	return activeLinks

def lspPacketHandler(pkt, pktArray):
	# [0]LSP [1]Sender Name [2]Sequence Number [3..N]Adjacent Active Links in pairs [Neighbor Name, Link Cost]
	# [3]Neighbor 1 Name [4]Link Cost to Neighbor 1 [5]Neighbor 2 Name [6]Link Cost to Neighbor 2 [...]
	print("Received a LSP packet from {0}".format(pktArray[1]))

	if neighborsTable.contains(pktArray[1]):
		# Convert Adjacent Active Links pair in 2 dimension table lsdUpdate[Neighbor][LinkCost]
		activeLinks = activeLinkPairsHandler(pktArray)
		if linkStateDatabase.contains(pktArray[1]):
			if pktArray[2] > linkStateDatabase.getSeqNumber(pktArray[1]):
				# Update existing entries in the LSDB
				linkStateDatabase.updateEntries(pktArray[1], activeLinks, pktArray[2])
		else:
			# Insert new entries in the LSDB
			linkStateDatabase.insertEntries(pktArray[1], activeLinks, pktArray[2])
		# send LSACK to sender
		# forward received LSDU to all other neighbors
		# launch SPF recalculation
	print(linkStateDatabase)	# debug

def packetTreatment(pkt):
	pktArray = (pkt[Raw].load).split()
	if pktArray[0] == "HELLO":
		helloPacketHandler(pkt, pktArray)
	if pktArray[0] == "LSP":
		lspPacketHandler(pkt, pktArray)

def packetCallback(pkt):
	if UDP in pkt:
		if pkt[UDP].dport == ROUTER_PORT:
			#print(pkt[Raw].load) # debug statement
			packetTreatment(pkt)
def launch():
	# launch packet sniffing continuously, listening to any received packets
	sniff(prn=packetCallback, store=0)

if __name__== "__main__":
	launch()
