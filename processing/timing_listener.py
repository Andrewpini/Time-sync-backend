from utils import Interval
import sys
import getopt
import time
import socket
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 10000

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))

participants = {}

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def animate(i):
    print("tjohei")
    ax1.clear()

    #for p_id, p_info in participants.items():
      #  for key in p_info:
           # print(key + ':', p_info[key])
          #  ax1.plot(key["x_coordinate"], key["y_coordinate"])

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.ion()

def send_server_info(ip):
    message = "CONTROL_COMMAND:" + chr(10) + chr(32) + "position_server: " + ip + ":" + str(LISTEN_PORT)
    broadcastSocket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))


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

   # ani = animation.FuncAnimation(fig, animate, interval=1000)
   # plt.ion()
   # plt.show()

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
                #print(participants[ip])
            else:
                participants[ip] = {"Farge": 'grønn', "x_coordinate": [], "y_coordinate": []}
                #print(participants)

        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break


if __name__ == "__main__":
    main(sys.argv[1:])
