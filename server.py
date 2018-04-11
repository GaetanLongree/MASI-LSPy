# here is the principal file of sfp project
import configparser
from sfp_alogrithm import *
from message import *
from hello_packet import *

config = configparser.ConfigParser()
config.read('config.ini')

if config['CONFIG']['ROUTER_NAME'] == "":
    raise ValueError('config is not edited, please change it')

HELLO_DELAY = 5000
MAX_LSP_DELAY = 30000
ROUTER_NAME = config['CONFIG']['ROUTER_NAME']
ROUTER_PORT = config['CONFIG']['ROUTER_PORT']

neighbor = []
# [0]name [1]ip address [2]port [3]cost
flag = True
nb_neig = 1
while flag:
    name = "NEIGHBOR_" + str(nb_neig)
    try:
        test = config['CONFIG'][name]
        text_Split = test.split(" ")
        neighbor.append(text_Split)
        nb_neig += 1
    except KeyError:
        flag = False
        pass
print (neighbor)

while True:
    lsp_packet.update()
    hello_packet.send()