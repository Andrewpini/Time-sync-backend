from utils import Interval
import sys, getopt
import socket
import json
import pymysql
from calc import distance
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

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
    nodes = dict()

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

                print("IP: ", ip, "\tAddress: ", address, "\tFiltered RSSI: ", nodes[ip][address]["filteredRssi"])

                nodes[ip][address]["rssi"] = list()
                
            if printing:
                print(counter , "\tFrom", ip, "\tTimestamp: ", timestamp, "\tCounter: ", counter, "\tAddr.: ", address, "\tChannel: ", channel, "\tRSSI: ", rssi, "\tCRC: ", crc, "\tLPE: ", lpe) 

        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break

if __name__ == "__main__":
   main(sys.argv[1:])
