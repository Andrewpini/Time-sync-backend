import sys, getopt
import socket
import json
import pymysql
import numpy as np
sys.path.insert(0,'..')
from calc import distance
from utils import Interval

DB_ENABLED = True
GRAPH_ENABLED = False

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
    channel = False
    distance = None
    label = None
    sampleNumber = 0
    samples = dict()
    samples["channel_37"] = list()
    samples["channel_38"] = list()
    samples["channel_39"] = list()

    opts, args = getopt.getopt(argv,"cdghil:o",["channel=", "distance=", "graph=", "ip=", "label="])
    del(args)

    if len(opts) == 0:
        print("A distance and label must be set for the test to start: general.py --distance <distance> --label '<label>'")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("A distance and label must be set for the test to start: general.py --distance <distance> --label '<label>'")
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
            print(ip)
        elif opt in ("-d", "--distance"):
            distance = float(arg)
            print("Test for distance: ", distance)
        elif opt in ("-l", "--label"):
            label = arg
            print("Label for test: ", label)
        elif opt in ("-c", "--channel"):
            channel = int(arg)
        elif opt in ("-g", "--graph"):
            GRAPH_ENABLED = True
        else:
            print("A distance and label must be set for the test to start: general.py --distance <distance> --label '<label>'")
            sys.exit(2)

    if not distance or not label:
        print("A distance and label must be set for the test to start: general.py --distance <distance> --label '<label>'")
        sys.exit(2)
 
    if GRAPH_ENABLED:
        import matplotlib.pyplot as plt
        plt.ion()
        plt.axis([36, 40, -80, -20])
        
        plt.legend(loc="lower right")

    interval = Interval.Interval(2, sendServerInfo, args=[ip,])
    print("Starting... Press CTRL + C to stop.")
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

            if DB_ENABLED:
                sql = "INSERT INTO rssi_data VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, NULL, %f, NULL, %d, %d, %d, '%s')" % (nodeID, ip, timestamp , address, channel, counter, rssi, distance, crc, lpe, syncController, label)

                cursor.execute(sql)
                db.commit()

            if GRAPH_ENABLED:
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
                
                plt.scatter(channel, rssi, color=color, alpha=0.1, label=name)
                plt.pause(0.0001)

            sampleNumber += 1

            if crc == 0:
                colorCode = "\u001b[31m"
            else:
                colorCode = ""

            print(colorCode, sampleNumber , "\tFrom", ip, "\tTimestamp: ", timestamp, "\tCounter: ", counter, "\tAddr.: ", address, "\tChannel: ", channel, "\tRSSI: ", rssi, "\tCRC: ", crc, "\tLPE: ", lpe, "\033[0m")

            if channel == 37:
                samples["channel_37"].append(rssi)
            elif channel == 38:
                samples["channel_38"].append(rssi)
            elif channel == 39:
                samples["channel_39"].append(rssi)

        except KeyboardInterrupt:
            print("")
            print("Standard deviation for channel 37 after ", len(samples["channel_37"]), " samples: ", np.std(samples["channel_37"], ddof=1))
            print("Standard deviation for channel 38 after ", len(samples["channel_38"]), " samples: ", np.std(samples["channel_38"], ddof=1))
            print("Standard deviation for channel 39 after ", len(samples["channel_39"]), " samples: ", np.std(samples["channel_39"], ddof=1))
            print("")
            print("Shutting down...")
            interval.stop()
            break

if __name__ == "__main__":
   main(sys.argv[1:])
