import datetime
import threading
import time
#import copy
from data_structures import *
from spf_algorithm import *

class AdjacencyMonitorThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.stopMonitor = threading.Event()

	def run(self):
		time.sleep(config.maxLSPDelay/2)
		while self.stopMonitor.isSet() != True:
			time.sleep(10)
			#copyAdjacencyTable = copy.deepcopy(adjacencyTable)
			adjacencyTable.acquire()
			for key in adjacencyTable:
				if adjacencyTable[key] is None:
					# removing dead neighbor from adjacency
					adjacencyTable.remove(key)
					linkStateDatabase.acquire()
					linkStateDatabase.removeEntries(key)
					linkStateDatabase.release()
					spf.run()
			adjacencyTable.release()

	def stop(self, timeout=None):
		self.stopMonitor.set()
		adjacencyTable.release()
		linkStateDatabase.release()
		super().join(timeout)
