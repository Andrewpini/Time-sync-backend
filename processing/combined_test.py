from utils import Interval
import sys, getopt
import socket
import json
import pymysql
from calc import distance
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from calc import multilateration as multi
import matplotlib.pyplot as plt

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 10000


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Tag:
    def __init__(self, address="", currentCounter=0, currentCounterAdvCount=0):
        self.address = address
        self.currentCounter = currentCounter
        self.currentCounterAdvCount = currentCounterAdvCount
        self.rssi = list()
        self.filteredRssi = 0
        self.distance = 0
        self.kalman = KalmanFilter(dim_x=1, dim_z=1)
        self.kalman.x = np.array([[-30.]])
        self.kalman.F = np.array([[1.]])
        self.kalman.H = np.array([[1.]])
        self.kalman.P = np.array([[0.]])
        self.kalman.R = 1.4
        self.kalman.Q = 0.065

    def setKalmanParameters(self, x, F, H, P, R, Q, dim_x=1, dim_z=1):
        self.kalman = KalmanFilter(dim_x=dim_x, dim_z=dim_z)
        self.kalman.x = x
        self.kalman.F = F
        self.kalman.H = H
        self.kalman.P = P
        self.kalman.R = R
        self.kalman.Q = Q

class Node:
    def __init__(self, nodeID, x=0, y=0):
        self.nodeID = nodeID
        self.position = Position(x, y)
        self.tags = dict()
        
nodes = dict()
nodes["93:94:07:73:96:1e"] = Node(nodeID="93:94:07:73:96:1e", x=2, y=0)
nodes["63:c3:af:19:3d:a0"] = Node(nodeID="63:c3:af:19:3d:a0", x=0, y=0)
nodes["88:eb:88:71:90:e8"] = Node(nodeID="88:eb:88:71:90:e8", x=0, y=2)

tags = dict()

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))
times = {}

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def sendServerInfo(ip):
    message = "CONTROL_COMMAND:" + chr(10) + chr(32) + "position_server: " + ip + ":" + str(LISTEN_PORT)
    broadcastSocket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))

def main(argv):
    global nodes
    opts, args = getopt.getopt(argv,"cghi:o",["channel=", "graph=", "ip=","addr=", "address="])
    del(args)
    totalCounter = 0

    if len(opts) == 0:
        print("udp_listener.py -i <server IP address>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("udp_listener.py -i <server IP address>")
            sys.exit()
        elif opt in ("-i", "-a", "--ip", "--address"):
            ip = arg
            print(ip)
        else:
            print("udp_listener.py -i <server IP address>")
            sys.exit(2)

    interval = Interval.Interval(2, sendServerInfo, args=[ip,])
    print("Starting Interval, press CTRL+C to stop.")
    interval.start() 

    # Initiate figure 
    fig = plt.figure()
    plt.ion()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim((-5, 5))
    ax.set_ylim((-5, 5))
    x0,x1 = ax.get_xlim()
    y0,y1 = ax.get_ylim()
    ax.set_aspect(abs(x1-x0)/abs(y1-y0))

    while True:
        try:
            rawData, addr = listenSocket.recvfrom(1024)
            data = json.loads(rawData)
            ip = addr[0]
            nodeID = data['nodeID']
            timestamp = data['timestamp']
            address = data['address']
            rssi = data['RSSI']
            crc = data['CRC']
            lpe = data['LPE']
            counter = data['counter']
            times[ip] = timestamp

            if crc == 1 and lpe == 0:
                if nodeID not in nodes: 
                    nodes[nodeID] = Node(nodeID)
                
                if address not in nodes[nodeID].tags: 
                    nodes[nodeID].tags[address] = Tag(address)
                    nodes[nodeID].tags[address].currentCounter = counter
                    nodes[nodeID].tags[address].currentCounterAdvCount  = 0
                    if address not in tags:
                        tags[address] = 1

                if nodes[nodeID].tags[address].currentCounter == counter:
                    nodes[nodeID].tags[address].currentCounterAdvCount += 1
                else:
                    nodes[nodeID].tags[address].currentCounter = counter
                    nodes[nodeID].tags[address].currentCounterAdvCount = 1
                
                if nodes[nodeID].tags[address].currentCounterAdvCount == 3:
                    nodes[nodeID].tags[address].rssi.append(rssi) 
                    selectedChannelRssi = max(nodes[nodeID].tags[address].rssi)

                    nodes[nodeID].tags[address].kalman.predict()
                    nodes[nodeID].tags[address].kalman.update(selectedChannelRssi)
                    filteredRssi = nodes[nodeID].tags[address].kalman.x[0]
                    nodes[nodeID].tags[address].filteredRssi = filteredRssi

                    # Log-distance path loss model
                    nodes[nodeID].tags[address].distance = round(distance.logDistancePathLoss(filteredRssi, rssi_d0=-40.0, d0=1.0, n=2.6, xo=1.1), ndigits=2)

                    print("node ID: ", nodeID, "\tIP: ", ip, "\tAddress: ", address, "\tFiltered RSSI: ", nodes[nodeID].tags[address].filteredRssi, "\tDistance: ", nodes[nodeID].tags[address].distance)

                    nodes[nodeID].tags[address].rssi = list()
                    totalCounter += 1
                
                if totalCounter > 0 and totalCounter % 20 == 0:
                    ax.cla()
                    ax.set_xlim((-3, 5))
                    ax.set_ylim((-3, 5))
                    plt.grid()
                    color = "b"
                    
                    for tagAddress in tags:
                        positions = list()
                        if color == "b":
                            color = "k"
                        else:
                            color = "b"

                        for _, node in nodes.items():
                            x = node.position.x
                            y = node.position.y
                            radius = node.tags[tagAddress].distance
                            positions.append((x, y, radius))


                            circle = plt.Circle((x, y), radius=radius, color=color, alpha=0.1)
                            center = plt.Circle((x, y), radius=0.1, color='r', alpha=1)
                            ax.add_patch(circle)
                            ax.add_patch(center)
                        
                        if len(positions) > 2:
                            position = multi.multilateration(positions)
                            tags[tagAddress] = position
                        
                        positionIndicator = plt.Circle(tags[tagAddress], radius=0.15, color=color, alpha=1)
                        ax.add_patch(positionIndicator)

                    plt.draw()
                    plt.pause(0.0001)
                    
        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break

if __name__ == "__main__":
   main(sys.argv[1:])
