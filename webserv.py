# -*- coding: utf-8 -*-
import socket
from data_structures import *
import threading


class WebServThread(threading.Thread):
    HOST, PORT = '', 80

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind((self.HOST, self.PORT))
        listen_socket.listen(1)
        print('Serving HTTP on port %s ...\n' % self.PORT)
        while True:
            client_connection, client_address = listen_socket.accept()
            request = client_connection.recv(1024)

            http_response = """<html><head><title>ROUTER: {}</title></head><style></style><body>

            <div style='display: flex;justify-content: space-around;'>
            <div style='padding: 10px 50px;width:600px;height:200px'>{}</div>
            <div style='padding: 10px 50px;width:600px;height:200px'>{}</div>
            </div>
            <div style='display: flex;justify-content: space-around;'>
            <div style='padding: 10px 50px;width:600px;height:200px'>{}</div>
            <div style='padding: 10px 50px;width:600px;height:200px'>{}</div>
            </div>
            <div style='display: flex;justify-content: space-around;'>
            <div style='padding: 10px 50px;width:600px;height:200px'>{}</div>
            <div style='padding: 10px 50px;width:600px;height:200px'>{}</div>
            </div><center><footer>Jean-Cyril Bohy et Gaetan Longree </br> Henallux Masi</footer></center>
            </body></html>
            """.format(config.routerName,config.web(),neighborsTable.web(),adjacencyTable.web(),linkStateDatabase.web(),lSUSentTable.web(),routingTable.web())

            client_connection.sendall(str.encode(http_response))
            client_connection.close()
