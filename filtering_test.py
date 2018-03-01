from utils import Interval
import sys, getopt
import socket
import json
import pymysql
from calc import distance
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise


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
    #db = pymysql.connect(host = "positioning.cbgkbhphknqn.us-east-2.rds.amazonaws.com", user = "jtguggedal", passwd = "", db = "positioning_db", port = #3306, cursorclass = pymysql.cursors.DictCursor)
    db = pymysql.connect(host = "localhost", user = "root", passwd = "admin", db = "positioning", port = 3306, cursorclass = pymysql.cursors.DictCursor)

    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    print("Connected to database")


def sendServerInfo(ip):
    message = "position_server: " + ip + ":" + str(LISTEN_PORT)
    broadcastSocket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))

def main(argv):
    channel = False
    global GRAPH_ENABLED
    opts, args = getopt.getopt(argv,"cghi:o",["channel=", "graph=", "ip=","addr=", "address="])
    del(args)
    counter = 0
    raw_rssi = list()
    filtered_rssi = list()
    dist = list()

    kalman = KalmanFilter(dim_x=1, dim_z=1)
    kalman.x = np.array([[-30.]])
    kalman.F = np.array([[1.]])
    kalman.H = np.array([[1.]])
    kalman.P = np.array([[0.]])
    kalman.R = 1.4
    kalman.Q = 0.065

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
    
    if GRAPH_ENABLED:
        import matplotlib.pyplot as plt
        plt.ion()
        #plt.axis([0, 100, -100, 0])
        #x = np.linspace(0, 2, 100)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.legend(loc="lower right")

    interval = Interval.Interval(2, sendServerInfo, args=[ip,])
    print("Starting Interval, press CTRL+C to stop.")
    interval.start() 

    while True:
        try:
            rawData, addr = listenSocket.recvfrom(1024)
            data = json.loads(rawData)
            printing = False

            #delta = data['timestamp'] - times[addr[0]]
            times[addr[0]] = data['timestamp']

            if DB_ENABLED:
                sql = "INSERT INTO rssi_data VALUES(NULL, '%s', '%d', '%s', %d, %d, %d, %d, NULL)" % (addr[0], data['timestamp'] , data['address'], data['channel'], data['RSSI'], data['CRC'], data['LPE'])

                cursor.execute(sql)
                db.commit()
            
            #dist = distance.empiricalDistance(data['RSSI'], 4, -45.0)


            if GRAPH_ENABLED and data['channel'] == 37:
                if addr[0] == "10.0.0.11":
                    kalman.predict()
                    kalman.update(data['RSSI'])
                    filtered_rssi.append(kalman.x[0])
                    counter += 1
                    color = 'r'
                    dist.append(round(counter / 2))
                    raw_rssi.append(data['RSSI'])
                    

                    plt.axis([0, dist[-1] + 20, -100, 0])
                    #plt.scatter(dist, data['RSSI'], color=color, alpha=0.5)
                    #ax.plot(dist, data['RSSI'], linestyle='-', color="b", linewidth=3, label="Raw")
                    color = 'g'
                    #plt.scatter(dist, filtered_rssi, color=color, alpha=0.5)
                    ax.plot(dist, raw_rssi, 'r-', label="Raw")
                    ax.plot(dist, filtered_rssi, 'b-', label="Kalman", linewidth=3)

                    if counter % 2 == 0:
                        plt.draw()
                        plt.pause(0.0001)
                    if counter == 1:
                        plt.legend(loc="lower right")



            if channel != False:
                if int(data['channel']) == channel:
                    printing = True
            else:
                printing = True

            if printing:
                print(counter , "\tFrom", addr[0], "\tTimestamp: ", times[addr[0]], "\tCounter: ", data['counter'], "\tAddr.: ", data['address'], "\tChannel: ", data['channel'], "\tRSSI: ", data['RSSI'], "\tCRC: ", data['CRC'], "\tLPE: ", data['LPE']) 

        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break

if __name__ == "__main__":
   main(sys.argv[1:])
