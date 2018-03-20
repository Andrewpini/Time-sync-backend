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
    nodes["10.0.0.11"] = dict()
    nodes["10.0.0.12"] = dict()
    nodes["10.0.0.14"] = dict()
    nodes["10.0.0.11"]["position"] = dict()
    nodes["10.0.0.12"]["position"] = dict()
    nodes["10.0.0.14"]["position"] = dict()
    nodes["10.0.0.11"]["position"]["x"] = 2
    nodes["10.0.0.11"]["position"]["y"] = 0
    nodes["10.0.0.12"]["position"]["x"] = 0
    nodes["10.0.0.12"]["position"]["y"] = 0
    nodes["10.0.0.14"]["position"]["x"] = 0
    nodes["10.0.0.14"]["position"]["y"] = 2

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
            timestamp = data['timestamp']
            address = data['address']
            channel = data['channel']
            rssi = data['RSSI']
            crc = data['CRC']
            lpe = data['LPE']
            counter = data['counter']
            times[ip] = timestamp

            if ip not in nodes: 
                nodes[ip] = dict()
            
            if address not in nodes[ip]: 
                nodes[ip][address] = dict()
                nodes[ip][address]["currentCounter"] = counter
                nodes[ip][address]["currentCounterAdvCount"] = 0
                nodes[ip][address]["rssi"] = list()

            if "kalman" not in nodes[ip][address]:
                nodes[ip][address]["kalman"] = KalmanFilter(dim_x=1, dim_z=1)
                nodes[ip][address]["kalman"].x = np.array([[-30.]])
                nodes[ip][address]["kalman"].F = np.array([[1.]])
                nodes[ip][address]["kalman"].H = np.array([[1.]])
                nodes[ip][address]["kalman"].P = np.array([[0.]])
                nodes[ip][address]["kalman"].R = 1.4
                nodes[ip][address]["kalman"].Q = 0.065

            if nodes[ip][address]["currentCounter"] == counter:
                nodes[ip][address]["currentCounterAdvCount"] += 1
            else:
                nodes[ip][address]["currentCounter"] = counter
                nodes[ip][address]["currentCounterAdvCount"] = 1
            
            if nodes[ip][address]["currentCounterAdvCount"] == 3:
                nodes[ip][address]["rssi"].append(rssi) 
                selectedChannelRssi = max(nodes[ip][address]["rssi"])

                nodes[ip][address]["kalman"].predict()
                nodes[ip][address]["kalman"].update(selectedChannelRssi)
                nodes[ip][address]["filteredRssi"] = nodes[ip][address]["kalman"].x[0]

                # Log-distance path loss model parameters
                rssi_d0 = -40.0
                d0 = 1.0
                n = 2.6
                xo = 1.1
		        
                nodes[ip][address]["distance"] = round(distance.logDistancePathLoss(nodes[ip][address]["filteredRssi"], rssi_d0, d0, n, xo), 2)

                print("IP: ", ip, "\tAddress: ", address, "\tFiltered RSSI: ", nodes[ip][address]["filteredRssi"], "\tDistance: ", nodes[ip][address]["distance"])

                nodes[ip][address]["rssi"] = list()
                totalCounter += 1
            
            if totalCounter > 0 and totalCounter % 10 == 0:
                position = multi.multilateration({  (nodes["10.0.0.11"]["position"]["x"], nodes["10.0.0.11"]["position"]["y"], nodes["10.0.0.11"][address]["distance"]), 
                                                    (nodes["10.0.0.12"]["position"]["x"], nodes["10.0.0.12"]["position"]["y"], nodes["10.0.0.12"][address]["distance"]),
                                                    (nodes["10.0.0.14"]["position"]["x"], nodes["10.0.0.14"]["position"]["y"], nodes["10.0.0.14"][address]["distance"])
                                                })

                circ1 = plt.Circle((nodes["10.0.0.11"]["position"]["x"], nodes["10.0.0.11"]["position"]["y"]), radius=nodes["10.0.0.11"][address]["distance"], color='b', alpha=0.1)
                circ2 = plt.Circle((nodes["10.0.0.11"]["position"]["x"], nodes["10.0.0.11"]["position"]["y"]), radius=0.01, color='r', alpha=1)
                circ3 = plt.Circle((nodes["10.0.0.12"]["position"]["x"], nodes["10.0.0.12"]["position"]["y"]), radius=nodes["10.0.0.12"][address]["distance"], color='b', alpha=0.1)
                circ4 = plt.Circle((nodes["10.0.0.12"]["position"]["x"], nodes["10.0.0.12"]["position"]["y"]), radius=0.01, color='r', alpha=1)
                circ5 = plt.Circle((nodes["10.0.0.14"]["position"]["x"], nodes["10.0.0.14"]["position"]["y"]), radius=nodes["10.0.0.14"][address]["distance"], color='b', alpha=0.1)
                circ6 = plt.Circle((nodes["10.0.0.14"]["position"]["x"], nodes["10.0.0.14"]["position"]["y"]), radius=0.01, color='r', alpha=1)
                ax.cla()
                ax.set_xlim((-5, 5))
                ax.set_ylim((-5, 5))
                ax.add_patch(circ1)
                ax.add_patch(circ2)    
                ax.add_patch(circ3)
                ax.add_patch(circ4) 
                ax.add_patch(circ5)
                ax.add_patch(circ6)
		
                circ = plt.Circle(position, radius=0.15, color='r', alpha=1)
                ax.add_patch(circ)
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
