from util import Interval
import sys, getopt
import socket
import json
import pymysql

DB_ENABLED = True

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
    opts, args = getopt.getopt(argv,"hi:o",["ip=","addr=", "address="])
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

            #delta = data['timestamp'] - times[addr[0]]
            times[addr[0]] = data['timestamp']
            print(counter , "\tFrom", addr[0], "\tTimestamp: ", times[addr[0]], "\tCounter: ", data['counter'], "\tAddr.: ", data['address'], "\tChannel: ", data['channel'], "\tRSSI: ", data['RSSI'], "\tCRC: ", data['CRC'], "\tLPE: ", data['LPE']) 

            if DB_ENABLED:
                sql = "INSERT INTO rssi_data VALUES(NULL, '%s', '%d', '%s', %d, %d, %d, %d, NULL)" % (addr[0], data['timestamp'] , data['address'], data['channel'], data['RSSI'], data['CRC'], data['LPE'])

                number_of_rows = cursor.execute(sql)
                db.commit()
        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break

if __name__ == "__main__":
   main(sys.argv[1:])
