import sys, getopt
import socket
import json
import pymysql
import jsonpickle
sys.path.insert(0,'..')
from calc import distance
from utils import Interval
import numpy as np
from positioning.positioning import Tag, Node, Position
from calc import multilateration as multi
from calc import distance
from utils import setup

# Configuration
DB_ENABLED              = True                          # Stores all data to database
DB_TABLE                = "position_testing_demo"       # Table name for wehre to store data
GRAPH_ENABLED           = True                          # Display real-time tracking graphics
NUMBER_OF_NODES_TO_USE  = 3                             # Number of nodes to use in the positioning algorithm, uses n nodes with shortest ditance to tag


POSITION_DIMENSIONS     = 3
defaultTxPower          = 0

SAMPLES_FOR_EACH_UPDATE = 20

# Log-distance path loss model config
LOG_DISTANCE_ST_DEV     = 0.0
LOG_DISTANCE_N          = 1.78
LOG_DISTANCE_RSSI_D0    = -38.0
LOG_DISTANCE_D0         = 1.0

# Network config
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 10000

# Make JSON object of settings to store in database
settings = "{ \"numberOfNodes\" : %d, \"dimensions\" : %d, \"logDistanceStdDev\" : %f, \"logDistanceN\" : %f, \"logDistanceRssiD0\" : %f , \"logDistanceD0\" : %f }" % (NUMBER_OF_NODES_TO_USE, POSITION_DIMENSIONS, LOG_DISTANCE_ST_DEV, LOG_DISTANCE_N, LOG_DISTANCE_RSSI_D0, LOG_DISTANCE_D0)

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
    allPositions = dict()
    setupEnable = True
    truePosition = Position(0, 0, 0)
    tagColor = ["b", "y", "c"]

    opts, args = getopt.getopt(argv,"cdfghilsxyz:o",["channel=", "database=", "filter=", "graph=", "ip=", "label=", "setup=", "x=", "y=", "z="])
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
        elif opt in ("-d", "--database"):
            DB_ENABLED = True
        elif opt in ("-s", "--setup"):
            if str(arg) == "true":
                setupEnable = True
            else :
                configFile = str(arg)
        elif opt in ("-x", "--trueX"):
            print("x: ", arg)
            truePosition.x = float(arg)
        elif opt in ("-y", "--trueY"):
            truePosition.y = float(arg)
        elif opt in ("-z", "--trueZ"):
            truePosition.z = float(arg)
        else:
            print("A label must be set for the test to start: filter_test.py --label '<label>'")
            sys.exit(2)
    if truePosition.x == 0 and truePosition.y == 0 and truePosition.z == 0:
        truePosition = "NULL"
    else:
        truePosition = (truePosition.x, truePosition.y, truePosition.z)
        print(truePosition)
    if not label:
        print("A label must be set for the test to start: filter_test.py --label '<label>'")
        sys.exit(2)
   
    interval = Interval.Interval(2, sendServerInfo, args=[ip,])
    print("Starting positioning test... Press CTRL + C to stop.")
    interval.start() 

    if setupEnable:
        # Run configuration of node setup
        setupConfig = dict()
        setupConfig["listenSocket"] = listenSocket
        setupConfig["broadcastSocket"] = broadcastSocket

        nodes = setup.setupNodes(setupConfig, fromFile=False) 
        configFile = "nodeConfig.txt"
        print(nodes)
    else:
        nodes = setup.setupNodes(None, fromFile=True, fileName=configFile)
        
    tags = dict()

    if GRAPH_ENABLED:
        import matplotlib.pyplot as plt
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.axis([-3, 10, -3, 10])

        ax.set_aspect(1)
        ax.grid(color='#cccccc', linestyle='-', linewidth=1)

        for _, node in nodes.items():
            node.setActiveStatus(False)


    while True:
        try:
            sql = ''
            rawData, addr = listenSocket.recvfrom(1024)
            data = json.loads(rawData)

            if not "nodeID" in data:
                continue

            ip = addr[0]
            nodeID = data['nodeID']
            timestamp = data['timestamp']
            address = data['address']
            if "txPower" in data:
                txPower = data['txPower']
            else:
                txPower = defaultTxPower
            rssi = data['RSSI']
            crc = data['CRC']
            lpe = data['LPE']
            counter = data['counter']
            syncController = data['syncController']
            channel = data['channel']
                    
            # Get true node position from config file or setup
            nodePosition = (nodes[nodeID].position.x, nodes[nodeID].position.y, nodes[nodeID].position.z)

            sql = "INSERT INTO `%s` VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, %d, NULL, %d, NULL, %d, %d, %d, '%s', '%s', NULL, NULL, '%s', '%s')" % (DB_TABLE, nodeID, ip, timestamp , address, channel, counter, txPower, rssi, 0, crc, lpe, syncController, label, configFile, nodePosition, settings)

            # If CRC or LPE fails, store to database and move on to next iteration
            if crc == 0 or lpe == 1:
                if DB_ENABLED:                    
                    sql = "INSERT INTO `%s` VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, %d, NULL, %d, NULL, %d, %d, %d, '%s', '%s', NULL, NULL, '%s', '%s')" % (DB_TABLE, nodeID, ip, timestamp , address, channel, counter, txPower, rssi, 0, crc, lpe, syncController, label, configFile, nodePosition, settings)
                    cursor.execute(sql)
                    db.commit()
                continue

            if nodeID not in nodes: 
                continue
                

            if address not in nodes[nodeID].tags: 
                nodes[nodeID].tags[address] = Tag(address)
                nodes[nodeID].tags[address].currentCounter = counter
                nodes[nodeID].tags[address].currentCounterAdvCount = 0
                if address not in tags:
                    tags[address] = (1, 1, 1)
                    allPositions[address] = list()

            nodes[nodeID].setActiveStatus(True)
            nodes[nodeID].tags[address].rssi.append(rssi) 
            
            if nodes[nodeID].tags[address].currentCounter == counter:
                nodes[nodeID].tags[address].currentCounterAdvCount += 1
                if DB_ENABLED:
                    sql = "INSERT INTO `%s` VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, %d, NULL, %d, NULL, %d, %d, %d, '%s', '%s', NULL, '%s', '%s', '%s')" % (DB_TABLE, nodeID, ip, timestamp , address, channel, counter, txPower, rssi, 0, crc, lpe, syncController, label, configFile, truePosition, nodePosition, settings)
            else:
                nodes[nodeID].tags[address].currentCounter = counter
                nodes[nodeID].tags[address].currentCounterAdvCount = 1

                selectedChannelRssi = max(nodes[nodeID].tags[address].rssi)

                nodes[nodeID].tags[address].kalman.predict()
                nodes[nodeID].tags[address].kalman.update(selectedChannelRssi)
                filteredRssi = nodes[nodeID].tags[address].kalman.x[0]
                nodes[nodeID].tags[address].filteredRssi = filteredRssi   
                nodes[nodeID].tags[address].rssi = list()         
            
                if DB_ENABLED:
                    sql = "INSERT INTO `%s` VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, %d, %f, %d, NULL, %d, %d, %d, '%s', '%s', NULL, '%s', '%s', '%s')" % (DB_TABLE, nodeID, ip, timestamp, address, channel, counter, txPower, rssi, filteredRssi, 0, crc, lpe, syncController, label, configFile, truePosition, nodePosition, settings)
            
            if totalCounter > 0 and totalCounter % 6 == 0:
                if GRAPH_ENABLED:
                    ax.cla()
                    ax.set_xlim((-5, 10))
                    ax.set_ylim((-5, 15))
                    plt.grid()
                
                tagKey = -1

                for tagAddress in tags:
                    tagKey += 1
                    positions = list()
                    color = 'k'

                    for _, node in nodes.items():
                        if node.getActiveStatus() == False or tagAddress not in node.tags:
                            continue
                        x = node.position.x
                        y = node.position.y
                        z = node.position.z
                                       
                        # Log-distance path loss model  
                        filteredRssi = node.tags[tagAddress].filteredRssi   
                        node.tags[tagAddress].distance = distance.logDistancePathLoss(filteredRssi, rssi_d0=LOG_DISTANCE_RSSI_D0, d0=LOG_DISTANCE_D0, n=LOG_DISTANCE_N, stDev=LOG_DISTANCE_ST_DEV)

                        radius = node.tags[tagAddress].distance
                        positions.append((x, y, z, radius))
                        if DB_ENABLED:
                            sql = "INSERT INTO `%s` VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, %d, %f, NULL, %f, %d, %d, %d, '%s', '%s', NULL, '%s', '%s', '%s')" % (DB_TABLE, nodeID, ip, timestamp, address, channel, counter, txPower, rssi, filteredRssi, radius, crc, lpe, syncController, label, configFile, truePosition, nodePosition, settings)

                        if GRAPH_ENABLED:
                            circle = plt.Circle((x, y), radius=radius, color=color, alpha=0.1)
                            center = plt.Circle((x, y), radius=0.1, color='r', alpha=1)
                            
                            ax.add_patch(circle)
                            ax.add_patch(center)
                    
                    if len(positions) >= NUMBER_OF_NODES_TO_USE:
                        sortedPositions = sorted(positions, key=lambda x: x[3])
                        estimatedPosition = multi.multilateration(sortedPositions[:NUMBER_OF_NODES_TO_USE], dimensions=POSITION_DIMENSIONS)
                        allPositions[tagAddress].append(estimatedPosition)
                        tags[tagAddress] = estimatedPosition

                        if truePosition != "NULL":
                            error_3d = np.sqrt(np.square(estimatedPosition[0] - truePosition[0]) + np.square(estimatedPosition[1] - truePosition[1]) + np.square(estimatedPosition[2] - truePosition[2]))
                        
                            error_2d = np.sqrt(np.square(estimatedPosition[0] - truePosition[0]) + np.square(estimatedPosition[1] - truePosition[1]))

                            ax.text(11, 3, ''.join(("Error 2D: ", str(round(error_2d, 2)))))
                            ax.text(11, 1, ''.join(("Error 3D: ", str(round(error_3d, 2)))))
                            print("x: ", round(estimatedPosition[0], 2), "\ty: ", round(estimatedPosition[1], 2), "\tz: ", round(estimatedPosition[2], 2), "\t Error 3D: ", round(error_3d, 2), "\tError 2D: ", round(error_2d, 2))

                        if DB_ENABLED:
                            sql = "INSERT INTO `%s` VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, %d, %f, NULL, %f, %d, %d, %d, '%s', '%s', '%s', '%s', '%s', '%s')" % (DB_TABLE, nodeID, ip, timestamp, address, channel, counter, txPower, rssi, filteredRssi, radius, crc, lpe, syncController, label, configFile, estimatedPosition, truePosition, nodePosition, settings)


                    
                        if GRAPH_ENABLED:
                            positionIndicator = plt.Circle(estimatedPosition, radius=0.20, color=tagColor[tagKey], alpha=1)
                            ax.add_patch(positionIndicator)

                            if truePosition != "NULL":
                                truePositionIndicator = plt.Circle(truePosition, radius=0.20, color="g", alpha=1)
                                ax.add_patch(truePositionIndicator)

                if GRAPH_ENABLED:
                    plt.draw()
                    plt.pause(0.0001)
            
            if DB_ENABLED:
                cursor.execute(sql)
                db.commit()
            totalCounter += 1

        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            if GRAPH_ENABLED: 

                ax.cla()
                ax.set_xlim((-5, 10))
                ax.set_ylim((-5, 15))
                plt.grid()
                for _, node in nodes.items():
                    x = node.position.x
                    y = node.position.y
                    z = node.position.z
                    center = plt.Circle((x, y), radius=0.1, color='r', alpha=1)
                    ax.add_patch(center)

                
                tagKey = -1
                for tagAddress in tags:
                    x = list()
                    y = list()
                    tagKey += 1
                    for position in allPositions[tagAddress][30:]:
                        x.append(position[0])
                        y.append(position[1])

                        plt.plot(x, y, '-', color=tagColor[tagKey], alpha=0.1)

                    if truePosition != "NULL":
                        truePositionIndicator = plt.Circle(truePosition, radius=0.20, color="g", alpha=1)
                        ax.add_patch(truePositionIndicator)

                plt.draw()
                plt.pause(0.0001)
                input("Press enter to exit")
            break

if __name__ == "__main__":
   main(sys.argv[1:])
