# here is the principal file of sfp project
import sys
from sfp_alogrithm import *
from message import *
from packet import *
from data_structures import *

config = Config()

if(sys.argv[1]):
    config.helloDelay = sys.argv[1]
    config.maxLSPDelay = sys.argv[2]
else:
    config.helloDelay = 5000
    config.maxLSPDelay = 60000



# Boucle de lancement
# while True:
