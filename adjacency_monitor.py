import datetime
import threading
import time
import datetime
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
			try:
				adjacencyTable.acquire()
				now = datetime.utcnow()
				for key in adjacencyTable:
					if (now - adjacencyTable[key].lastContact).total_seconds() > (4 * config.helloDelay):
						# removing dead neighbor from adjacency
						adjacencyTable.remove(key)
						linkStateDatabase.acquire()
						linkStateDatabase.removeEntries(key)
						linkStateDatabase.release()
				spf.run()
				adjacencyTable.release()
			except RuntimeError:
				adjacencyTable.release()

	def stop(self, timeout=None):
		self.stopMonitor.set()
		if adjacencyTable.lock.locked() == True:
			adjacencyTable.release()
		if linkStateDatabase.lock.locked() == True:
			linkStateDatabase.release()
		super().join(timeout)
