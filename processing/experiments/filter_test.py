import sys, getopt
import socket
import json
import pymysql
sys.path.insert(0,'..')
from calc import distance
from utils import Interval
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise


DB_ENABLED = True
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
    chosenChannel = None
    distance = None
    label = None
    sampleNumber = 0
    rawRssiList = list()
    filteredRssiList = list()
    xAxis= list()

    kalman = KalmanFilter(dim_x=1, dim_z=1)
    kalman.x = np.array([[-30.]])
    kalman.F = np.array([[1.]])
    kalman.H = np.array([[1.]])
    kalman.P = np.array([[0.]])
    kalman.R = 3.19
    kalman.Q = 0.065

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
        elif opt in ("-d", "--distance"):
            distance = int(arg)
            print("Test for distance: ", distance)
        elif opt in ("-l", "--label"):
            label = arg
            print("Label for test: ", label)
        elif opt in ("-c", "--channel"):
            chosenChannel = int(arg)
        elif opt in ("-g", "--graph"):
            GRAPH_ENABLED = True
        else:
            print("A label must be set for the test to start: filter_test.py --label '<label>'")
            sys.exit(2)

    if not distance or not label:
        print("A label must be set for the test to start: filter_test.py --label '<label>'")
        sys.exit(2)
 
    if GRAPH_ENABLED:
        import matplotlib.pyplot as plt
        #plt.ion()
        #plt.axis([0, distance * 2, -80, -20])
        
        #plt.legend(loc="lower right")


        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.grid(color='#cccccc', linestyle='-', linewidth=1)
        ax.legend(loc="lower right")

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

            if chosenChannel == channel and crc == 1 and lpe == 0:

                kalman.predict()
                kalman.update(rssi)
                filteredRssi = kalman.x[0]
                filteredRssiList.append(filteredRssi)
                xAxis.append(round(sampleNumber / 2))
                rawRssiList.append(data['RSSI'])
                plt.axis([0, xAxis[-1] + 20, -50, -20])
                if sampleNumber == 1:
                    plt.legend(loc="lower right")

                if DB_ENABLED:
                    sql = "INSERT INTO rssi_data VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, %f, %d, NULL, %d, %d, %d, '%s')" % (nodeID, ip, timestamp , address, channel, counter, rssi, filteredRssi, distance, crc, lpe, syncController, label)

                    cursor.execute(sql)
                    db.commit()

                if GRAPH_ENABLED and (sampleNumber % SAMPLES_FOR_EACH_UPDATE) == 0:
                    color = 'k'
                    name = "Unknown channel"
                    if channel == 37:
                        color = 'r'
                        name = "Channel 37"
                    elif channel == 38:
                        color = 'b'
                        name = "Channel 38"
                    elif channel == 39:
                        color = 'g'
                        name = "Channel 39"
                    
                    if PLOT_DISTANCE:
                        plt.scatter(distance, filteredRssi, color=color, alpha=0.1, label=name)
                        plt.scatter(distance, rssi, color='k', alpha=0.1, label=name)
                    elif PLOT_TIME:
                        ax.plot(xAxis, rawRssiList, 'r-', label="Raw", alpha=0.7)
                        ax.plot(xAxis, filteredRssiList, 'b-', label="Kalman", linewidth=3)
                    plt.pause(0.0001)

                sampleNumber += 1
                print(sampleNumber , "\tFrom", ip, "\tTimestamp: ", timestamp, "\tCounter: ", counter, "\tAddr.: ", address, "\tChannel: ", channel, "\tRSSI: ", rssi, "\tCRC: ", crc, "\tLPE: ", data['LPE']) 

        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break

if __name__ == "__main__":
   main(sys.argv[1:])
