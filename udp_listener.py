from utils import Interval
import sys, getopt
import socket
import json
import pymysql
import matplotlib.pyplot as plt
import numpy as np
from calc import distance


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
        plt.ion()
        fig = plt.figure()
        plt.axis([0, 3, -100, 0])
        i = 0
        
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
            

            dist = distance.empiricalDistance(data['RSSI'], 4, -45.0)

            if data['channel'] == 37:
                color = 'r'
            elif data['channel'] == 38:
                color = 'g'
            if data['channel'] == 39:
                color = 'b'

            if GRAPH_ENABLED and data['channel'] == 37:
                color = 'r'
                dist = distance.empiricalDistance(data['RSSI'], 4, -45.0)
                plt.scatter(dist, data['RSSI'], color=color, alpha=0.1)

                color = 'g'
                dist = distance.ituDistance(data['RSSI'], distance.bleChannelToFrequency(data['channel']), 30, 14.1, 1)
                plt.scatter(dist, data['RSSI'], color=color, alpha=0.1)

                color = 'b'
                dist = distance.logDistancePathLoss(data['RSSI'], -42.0, 1.0, 4, 0)
                plt.scatter(dist, data['RSSI'], color=color, alpha=0.1)
                #plt.show()
                plt.pause(0.0001)

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
