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
        x = test.split(" ")
        dict_neighbor = {'name': x[0], 'ip': x[1], 'port': x[2], 'cost': x[3]}
        neighbor.append(dict_neighbor)
        nb_neig += 1
    except KeyError:
        flag = False
        pass
print(neighbor)
hello_packet()
# Boucle de lancement
# while True:
