import sys, getopt
import socket
import json
import pymysql
sys.path.insert(0,'..')
from calc import distance
from utils import Interval
import numpy as np
from positioning.positioning import Tag, Node, Position
from calc import multilateration as multi
from calc import distance


DB_ENABLED = False
GRAPH_ENABLED = True
PLOT_TIME = True
PLOT_DISTANCE = False
SAMPLES_FOR_EACH_UPDATE = 20

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 10000

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

if DB_ENABLED:
    # Open database connection
    db = pymysql.connect(host = "localhost", user = "root", passwd = "admin", db = "positioning", port = 3306, cursorclass = pymysql.cursors.DictCursor)

    # Prepare a cursor object using cursor() method
    cursor = db.cursor()
    print("Connected to database")

# Server info (IP and port no.) is broadcasted at regular intervals
def sendServerInfo(ip):
    message = "CONTROL_COMMAND:" + chr(10) + chr(32) + "position_server: " + ip + ":" + str(LISTEN_PORT)
    broadcastSocket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))

def main(argv):
    global GRAPH_ENABLED
    global DB_ENABLED
    label = None
    totalCounter = 0

    opts, args = getopt.getopt(argv,"cdfghil:o",["channel=", "distance=", "filter=", "graph=", "ip=", "label="])
    del(args)

    if len(opts) == 0:
        print("A label must be set for the test to start: filter_test.py --label '<label>'")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("A label must be set for the test to start: filter_test.py --label '<label>'")
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
            print(ip)
        elif opt in ("-l", "--label"):
            label = arg
            print("Label for test: ", label)
        elif opt in ("-g", "--graph"):
            GRAPH_ENABLED = True
        else:
            print("A label must be set for the test to start: filter_test.py --label '<label>'")
            sys.exit(2)

    if not label:
        print("A label must be set for the test to start: filter_test.py --label '<label>'")
        sys.exit(2)

    nodes = dict()
    nodes["b0:94:07:73:96:1e"] = Node(nodeID="b0:94:07:73:96:1e", x=2, y=0)
    nodes["b0:c3:af:19:3d:a0"] = Node(nodeID="b0:c3:af:19:3d:a0", x=0, y=0)
    nodes["b0:44:d6:f0:48:65"] = Node(nodeID="88:eb:88:71:90:e8", x=0, y=2)

    tags = dict()

 
    if GRAPH_ENABLED:
        import matplotlib.pyplot as plt
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.axis([-3, 10, -3, 10])

        ax.set_aspect(1)
        ax.grid(color='#cccccc', linestyle='-', linewidth=1)

    interval = Interval.Interval(2, sendServerInfo, args=[ip,])
    print("Starting filter test... Press CTRL + C to stop.")
    interval.start() 

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
            syncController = data['syncController']
            channel = data['channel']

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
                    nodes[nodeID].tags[address].distance = round(distance.logDistancePathLoss(filteredRssi, rssi_d0=-40.0, d0=1.0, n=2.6, Xo=0.0), ndigits=2)

                    print("node ID: ", nodeID, "\tIP: ", ip, "\tAddress: ", address, "\tFiltered RSSI: ", nodes[nodeID].tags[address].filteredRssi, "\tDistance: ", nodes[nodeID].tags[address].distance)

                    nodes[nodeID].tags[address].rssi = list()
                    totalCounter += 1

                    if DB_ENABLED:
                        sql = "INSERT INTO rssi_data VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, %f, %d, NULL, %d, %d, %d, '%s')" % (nodeID, ip, timestamp , address, channel, counter, rssi, filteredRssi, 0, crc, lpe, syncController, label)

                        cursor.execute(sql)
                        db.commit()
                
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
                            z = node.position.z
                            radius = node.tags[tagAddress].distance
                            positions.append((x, y, z, radius))


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
