from scapy.all import *

def packetTreatment(pktLoad):
	pktArray = pktLoad.split()
	if pktArray[0] == "HELLO":
		# treat hello packet reception
		print("Received a HELLO packet from {0}".format(pktArray[2]))
	if pktArray[0] == "LSP":
		# treat lsp packet reception
		print("Received a LSP packet from {0}".format(pktArray[1]))

def packetCallback(pkt):
	if UDP in pkt:
		if pkt[UDP].dport == 30000:
			#print(pkt[Raw].load) # debug statement
			packetTreatment(pkt[Raw].load)

sniff(prn=packetCallback, store=0)
