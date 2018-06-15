import sys, getopt
import socket
import json
import pymysql
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
    trueDistance = None
    label = None
    model = None
    sampleNumber = 0

    opts, args = getopt.getopt(argv,"cdghilm:o",["channel=", "distance=", "graph=", "ip=", "label=", "model="])
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
            trueDistance = int(arg)
            print("Test for distance: ", trueDistance)
        elif opt in ("-l", "--label"):
            label = arg
            print("Label for test: ", label)
        elif opt in ("-m", "--model"):
            model = arg
            print("Model for testing: ", model)
        elif opt in ("-c", "--channel"):
            channel = int(arg)
        elif opt in ("-g", "--graph"):
            GRAPH_ENABLED = True
        else:
            print("A distance and label must be set for the test to start: general.py --distance <distance> --label '<label>'")
            sys.exit(2)

    if not trueDistance or not label:
        print("A distance and label must be set for the test to start: general.py --distance <distance> --label '<label>'")
        sys.exit(2)
 
    if GRAPH_ENABLED:
        import matplotlib.pyplot as plt
        plt.ion()
        plt.axis([0, trueDistance * 2, -80, -20])
        
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
                sql = "INSERT INTO rssi_data VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, NULL, %d, %d, %d, '%s')" % (nodeID, ip, timestamp , address, channel, counter, rssi, crc, lpe, syncController, label)

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
                
                plt.scatter(trueDistance, rssi, color=color, alpha=0.1, label=name)
                plt.pause(0.0001)

            sampleNumber += 1
            print(sampleNumber , "\tFrom", ip, "\tTimestamp: ", timestamp, "\tCounter: ", counter, "\tAddr.: ", address, "\tChannel: ", channel, "\tRSSI: ", rssi, "\tCRC: ", crc, "\tLPE: ", data['LPE']) 

        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break

if __name__ == "__main__":
   main(sys.argv[1:])
