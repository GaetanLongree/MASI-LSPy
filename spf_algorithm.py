from data_structures import *
import sys

class WeightedEntry:
    # NB: shortedDistance indicates the shortes distance from us
    def __init__(self, shortestDistance, previousNode):
        self.shortestDistance = shortestDistance
        self.previousNode = previousNode

class Graph(dict):

    def createEmpty(self):
        for key, value in linkStateDatabase.items():
            self[key] = WeightedEntry(sys.maxsize, None)
        self[config.routerName] = WeightedEntry(0,None)


    # returns the next node from the unvisited set with smallest distance
    def getNextUnvisitedNode(self, unvisitedNodes):
        minKey = min(unvisitedNodes, key=(lambda k: self[k].shortestDistance))
        return minKey

class SPF:
    def __init__(self):
        self.graph = Graph()
        self.graph.createEmpty()
        self.visitedNodes = []
        self.unvisitedNodes = list(self.graph.keys())

    def run(self):
        self.__init__()
        for x in range(0, len(self.graph)):
            currentNode = self.graph.getNextUnvisitedNode(self.unvisitedNodes)
            #print("Current node: " + currentNode) #debug

            # check the each current node's neighbors
            # sum the link cost, compare to cost in graph
            # insert in the graph if smaller + save previousNode
            for key, value in linkStateDatabase[currentNode].activeLinks.items():
                if key in self.graph:
                    sum = self.graph[currentNode].shortestDistance + int(value)
                    #print(currentNode + "-" + key + "=" + str(sum) + "(" + str(self.graph[currentNode].shortestDistance) + "+" + str(value) + ")") #debug
                    if sum < self.graph[key].shortestDistance:
                        self.graph[key].shortestDistance = sum
                        self.graph[key].previousNode = currentNode

            # move currentNode from unvisited to visited
            self.visitedNodes.append(currentNode)
            self.unvisitedNodes.remove(currentNode)
            #print("Visited Nodes:\n" + self.visitedNodes.__str__()) #debug
            #print("Unvisited Nodes:\n" + self.unvisitedNodes.__str__()) #debug

        routingTable.populateFromSPF(self.graph)


    def __str__(self):
        toString = "###SPF ALGORITHM RESULT###\nNode\tDistance\tPrevious Node\n"
        for key, value in self.graph.items():
            toString += key + "\t" + str(value.shortestDistance) + "\t\t" + str(value.previousNode) + "\n"
        return toString


spf = SPF()
