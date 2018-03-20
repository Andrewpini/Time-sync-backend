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

GRAPH_ENABLED = False

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 10000

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))
times = {}

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def sendServerInfo(ip):
    message = "CONTROL_COMMAND:" + chr(10) + chr(32) + "position_server: " + ip + ":" + str(LISTEN_PORT)
    broadcastSocket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))

def main(argv):
    channel = False
    global GRAPH_ENABLED
    opts, args = getopt.getopt(argv,"cghi:o",["channel=", "graph=", "ip=","addr=", "address="])
    del(args)
    totalCounter = 0
    nodes = dict()
    nodes["93:94:07:73:96:1e"] = dict()
    nodes["63:c3:af:19:3d:a0"] = dict()
    nodes["88:eb:88:71:90:e8"] = dict()
    nodes["93:94:07:73:96:1e"]["position"] = dict()
    nodes["63:c3:af:19:3d:a0"]["position"] = dict()
    nodes["88:eb:88:71:90:e8"]["position"] = dict()
    nodes["93:94:07:73:96:1e"]["position"]["x"] = 2
    nodes["93:94:07:73:96:1e"]["position"]["y"] = 0
    nodes["63:c3:af:19:3d:a0"]["position"]["x"] = 0
    nodes["63:c3:af:19:3d:a0"]["position"]["y"] = 0
    nodes["88:eb:88:71:90:e8"]["position"]["x"] = 0
    nodes["88:eb:88:71:90:e8"]["position"]["y"] = 2

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
        elif opt in ("-c", "--channel"):
            channel = int(arg)
        elif opt in ("-g", "--graph"):
            GRAPH_ENABLED = True
        else:
            print("udp_listener.py -i <server IP address>")
            sys.exit(2)

    interval = Interval.Interval(2, sendServerInfo, args=[ip,])
    print("Starting Interval, press CTRL+C to stop.")
    interval.start() 


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
            printing = False
            ip = addr[0]
            nodeID = data['nodeID']
            timestamp = data['timestamp']
            address = data['address']
            channel = data['channel']
            rssi = data['RSSI']
            crc = data['CRC']
            lpe = data['LPE']
            counter = data['counter']
            times[ip] = timestamp

            if crc == 1 and lpe == 0:
                if nodeID not in nodes: 
                    nodes[nodeID] = dict()
                
                if address not in nodes[nodeID]: 
                    nodes[nodeID][address] = dict()
                    nodes[nodeID][address]["currentCounter"] = counter
                    nodes[nodeID][address]["currentCounterAdvCount"] = 0
                    nodes[nodeID][address]["rssi"] = list()

                if "kalman" not in nodes[nodeID][address]:
                    nodes[nodeID][address]["kalman"] = KalmanFilter(dim_x=1, dim_z=1)
                    nodes[nodeID][address]["kalman"].x = np.array([[-30.]])
                    nodes[nodeID][address]["kalman"].F = np.array([[1.]])
                    nodes[nodeID][address]["kalman"].H = np.array([[1.]])
                    nodes[nodeID][address]["kalman"].P = np.array([[0.]])
                    nodes[nodeID][address]["kalman"].R = 1.4
                    nodes[nodeID][address]["kalman"].Q = 0.065

                if nodes[nodeID][address]["currentCounter"] == counter:
                    nodes[nodeID][address]["currentCounterAdvCount"] += 1
                else:
                    nodes[nodeID][address]["currentCounter"] = counter
                    nodes[nodeID][address]["currentCounterAdvCount"] = 1
                
                if nodes[nodeID][address]["currentCounterAdvCount"] == 3:
                    nodes[nodeID][address]["rssi"].append(rssi) 
                    selectedChannelRssi = max(nodes[nodeID][address]["rssi"])

                    nodes[nodeID][address]["kalman"].predict()
                    nodes[nodeID][address]["kalman"].update(selectedChannelRssi)
                    nodes[nodeID][address]["filteredRssi"] = nodes[nodeID][address]["kalman"].x[0]

                    # Log-distance path loss model parameters
                    rssi_d0 = -40.0
                    d0 = 1.0
                    n = 2.6
                    xo = 1.1
                    
                    nodes[nodeID][address]["distance"] = round(distance.logDistancePathLoss(nodes[nodeID][address]["filteredRssi"], rssi_d0, d0, n, xo), 2)

                    print("node ID: ", nodeID, "\tIP: ", ip, "\tAddress: ", address, "\tFiltered RSSI: ", nodes[nodeID][address]["filteredRssi"], "\tDistance: ", nodes[nodeID][address]["distance"])

                    nodes[nodeID][address]["rssi"] = list()
                    totalCounter += 1
                
                if totalCounter > 0 and totalCounter % 10 == 0:
                    positions = list()
                    ax.cla()
                    ax.set_xlim((-5, 5))
                    ax.set_ylim((-5, 5))

                    for _, node in nodes.items():
                        x = node["position"]["x"]
                        y = node["position"]["y"]
                        radius = node[address]["distance"]
                        positions.append((x, y, radius))

                        circle = plt.Circle((x, y), radius=radius, color='b', alpha=0.1)
                        center = plt.Circle((x, y), radius=0.01, color='r', alpha=1)
                        ax.add_patch(circle)
                        ax.add_patch(center)
                    
                    position = multi.multilateration(positions)
                    
                    positionIndicator = plt.Circle(position, radius=0.15, color='r', alpha=1)
                    ax.add_patch(positionIndicator)

                    plt.draw()
                    plt.pause(0.0001)
                    
                if printing:
                    print(counter , "\tFrom", ip, "\tTimestamp: ", timestamp, "\tCounter: ", counter, "\tAddr.: ", address, "\tChannel: ", channel, "\tRSSI: ", rssi, "\tCRC: ", crc, "\tLPE: ", lpe) 

        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break

if __name__ == "__main__":
   main(sys.argv[1:])
