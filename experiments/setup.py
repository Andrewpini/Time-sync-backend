import sys, getopt
import socket
import time
import json
sys.path.insert(0,'..')
from utils import Interval

TIME_TO_WAIT = 5

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 10000

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def sendMessage(message):
    broadcastSocket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))

def cmdWhoAmI(start=True):
    if start:
        cmd = "CONTROL_COMMAND:\x01\x00"
    else:
        cmd = "CONTROL_COMMAND:\x02\x00"
    sendMessage(cmd)

def cmdAllLedsOn(enable=True):
    if enable:
        cmd = "CONTROL_COMMAND:(\x00"
    else:
        cmd = "CONTROL_COMMAND:)\00"
    sendMessage(cmd)

def cmdSingleLedOn(ip, enable=True):
    ipArray = ip.split(".")
    formattedIp = '' + chr(int(ipArray[0])) + chr(int(ipArray[1])) + chr(int(ipArray[2])) + chr(int(ipArray[3])) 
    if enable:
        cmd = "CONTROL_COMMAND:2\x04" + formattedIp
    else:
        cmd = "CONTROL_COMMAND:3\x04" + formattedIp
    sendMessage(cmd)


def sendServerInfo(ip):
    message = "CONTROL_COMMAND:" + chr(10) + chr(32) + "position_server: " + ip + ":" + str(LISTEN_PORT)
    sendMessage(message)


def main(argv):
    nodes = dict()
    ip = None

    opts, _ = getopt.getopt(argv,"cdfghil:o",["channel=", "database=", "filter=", "graph=", "ip=", "label="])
    
    for opt, arg in opts:
        if opt == '-h':
            print("A label must be set for the test to start: filter_test.py --label '<label>'")
            sys.exit()
        elif opt in ("-i", "-a", "--ip", "--address"):
            ip = arg
            print(ip)

    if not ip:
        print("Please provide IP argument: setup.py --ip <IP address>")
        sys.exit()
    
    interval = Interval.Interval(2, sendServerInfo, args=[ip,])
    print("Starting Interval, press CTRL+C to stop.")
    interval.start() 

    time.sleep(1)

    cmdAllLedsOn(enable=True)
    cmdWhoAmI(start=True)

    endTime = time.time() + TIME_TO_WAIT

    while time.time() < endTime:
        try:
            rawData, _ = listenSocket.recvfrom(1024)
            data = json.loads(rawData)

            if "MAC" in data:
                mac = data["MAC"]
                ip = data["IP"]

                print("WHO AM I message from MAC", mac, ", IP is ", ip)
                if mac not in nodes:
                    nodes[mac] = dict()
                    nodes[mac]["MAC"] = mac
                    nodes[mac]["IP"] = ip
                continue


        except KeyboardInterrupt:
            print("Shutting down interval...")
            interval.stop()
            break
    
    cmdAllLedsOn(enable=False)
    cmdWhoAmI(start=False)

    print(f"\n\nAvailable nodes (%d):" % len(nodes))
    for _, node in nodes.items():
        print("\tMAC: ", node["MAC"], "\tIP: ", node["IP"])


    for key, node in nodes.items():
        cmdSingleLedOn(node["IP"], enable=True)
        x = input("Node's x-coordinate:")
        y = input("Node's y-coordinate:")
        z = input("Node's x-coordinate:")

        nodes[key]["x"] = x
        nodes[key]["y"] = y
        nodes[key]["z"] = z

        cmdSingleLedOn(node["IP"], enable=False)

    print("\n\nNode overview:")
    for _, node in nodes.items():
        print("\tMAC: ", node["MAC"], "\tIP: ", node["IP"], "\t\tx: ", node["x"], "\ty: ", node["y"], "\tz: ", node["z"])

    

if __name__ == "__main__":
   main(sys.argv[1:])
