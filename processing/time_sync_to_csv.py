import csv
import datetime

from utils import Interval
import sys
import getopt
import socket
import json



LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 10000

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))

participants = {}

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def send_server_info(ip):
    message = "CONTROL_COMMAND:" + chr(10) + chr(32) + "position_server: " + ip + ":" + str(LISTEN_PORT)
    broadcastSocket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))

now = datetime.datetime.now()
file_name = "raw_sync_data_" + now.strftime("%d-%m-%Y(%H_%M)") + ".csv"



with open(file_name, 'w', newline='') as csvfile:
    fieldnames = ['Event_ID', 'Node', 'Timestamp(in microsec)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    csvfile.close()
def main(argv):
    opts, args = getopt.getopt(argv, "cghilt:o", ["ip="])
    del args

    if len(opts) == 0:
        print("timing_listener.py -i <server IP address>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("timing_listener.py -i <server IP address>")
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
            print(ip)
        else:
            print("timing_listener.py -i <server IP address>")
            sys.exit(2)

    interval = Interval.Interval(2, send_server_info, args=[ip])
    print("Starting Interval, press CTRL+C to stop.")
    interval.start()


    while True:
        try:
            raw_data, addr = listenSocket.recvfrom(1024)
            data = json.loads(raw_data)
            ip = addr[0]
            event_id = data['timetic']
            timestamp = data['drift']

            with open(file_name, 'a', newline='') as csvfile:
                fieldnames = ['Event_ID', 'Node', 'Timestamp(in microsec)']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                thisdict = {"Event_ID": event_id, "Node": ip, "Timestamp(in microsec)": timestamp}
                print(thisdict)
                writer.writerow(thisdict)
                csvfile.close()



        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break


if __name__ == "__main__":
    main(sys.argv[1:])



