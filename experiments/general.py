import sys, getopt
import socket
import json
import pymysql
sys.path.insert(0,'..')
from calc import distance
import utils

DB_ENABLED = False
GRAPH_ENABLED = False

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 10000

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))
counter = 1
times = {}

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

    opts, args = getopt.getopt(argv,"cdghil:o",["channel=", "distance=", "graph=", "ip=", "label="])
    del(args)

    if len(opts) == 0:
        print("rssi_distance.py -i <server IP address>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("A distance and label must be set for the test to start: rssi_distance.py --distance <distance> --label '<label>'")
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
            print(ip)
        elif opt in ("-d", "--distance"):
            distance = arg
            print("Test for distance: ", distance)
        elif opt in ("-l", "--label"):
            label = arg
            print("Label for test: ", label)
        elif opt in ("-c", "--channel"):
            channel = int(arg)
        elif opt in ("-g", "--graph"):
            GRAPH_ENABLED = True
        else:
            print("A distance and label must be set for the test to start: rssi_distance.py --distance <distance> --label '<label>'")
            sys.exit(2)

    if not distance or not label:
        print("A distance and label must be set for the test to start: rssi_distance.py --distance <distance> --label '<label>'")
        sys.exit(2)
 
    if GRAPH_ENABLED:
        import matplotlib.pyplot as plt
        plt.ion()
        plt.axis([0, distance + 2, -100, 0])

    interval = utils.Interval.Interval(2, sendServerInfo, args=[ip,])
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

            #delta = data['timestamp'] - times[addr[0]]
            times[addr[0]] = data['timestamp']

            if DB_ENABLED:
                sql = "INSERT INTO rssi_data VALUES(NULL, NULL, '%s', '%s', %d, '%s', %d, %d, %d, %d, %d, '%s')" % (nodeID, ip, timestamp , address, channel, counter, rssi, crc, lpe, label)

                cursor.execute(sql)
                db.commit()

            if GRAPH_ENABLED:
                if channel == 37:
                    color = 'r'
                elif channel == 38:
                    color = 'b'
                elif color == 39:
                    color = 'g'
                
                plt.scatter(distance, rssi, color=color, alpha=0.1)
                plt.pause(0.0001)

            print(counter , "\tFrom", ip, "\tTimestamp: ", timestamp, "\tCounter: ", counter, "\tAddr.: ", address, "\tChannel: ", channel, "\tRSSI: ", rssi, "\tCRC: ", crc, "\tLPE: ", data['LPE']) 

        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break

if __name__ == "__main__":
   main(sys.argv[1:])
