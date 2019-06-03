from utils import Interval
import random
import sys
import getopt
import time
import socket
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


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


def create_plot():
    p = plt.figure(1).add_subplot(1, 1, 1)
    plt.ion()
    plt.show()
    plt.draw()
    plt.grid()
    return p



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

    plot = create_plot()

    while True:
        try:
            raw_data, addr = listenSocket.recvfrom(1024)
            data = json.loads(raw_data)
            ip = addr[0]
            timetic = data['timetic']
            drift = data['drift']
            print(addr[0], raw_data)

            if addr[0] in participants:
                participants[ip]["x_coordinate"].append(timetic)
                participants[ip]["y_coordinate"].append(drift)

                log_file = open("datadrift_log.txt", "a")
                log_file.write("Addr: " + str(ip) + " Time: " + str(timetic) + " Drift: " + str(drift) +"\n")
                log_file.close()
            else:
                participants[ip] = {"Farge": 'grønn', "x_coordinate": [], "y_coordinate": []}

            plot.clear()
            for participant in participants.values():
                plot.plot(participant['y_coordinate'])
            plt.draw()
            plt.pause(0.001)

        except KeyboardInterrupt:
            print("Shutting down interval...")
            log_file.close()
            interval.stop()
            break


if __name__ == "__main__":
    main(sys.argv[1:])




