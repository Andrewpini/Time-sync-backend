import sys, getopt
import socket
import time
import json
import jsonpickle
sys.path.insert(0,'..')
from utils import Interval
from positioning.positioning import Tag, Node, Position

TIME_TO_WAIT = 5

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

BROADCAST_IP = "255.255.255.255"
BROADCAST_PORT = 10000

listenSocket = None
#listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#listenSocket.bind((LISTEN_IP, LISTEN_PORT))

broadcastSocket = None
#broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def sendMessage(message):
    global listenSocket
    global broadcastSocket
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
        cmd = "CONTROL_COMMAND:)\x00"
    sendMessage(cmd)

def cmdAllLedsDefault():
    cmd = "CONTROL_COMMAND:\x2a"
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

    #setupNodes()


def setupNodes(config, fromFile=False, verbose=False, fileName=""):
    global listenSocket
    global broadcastSocket
    nodes = dict()

    try:
        if fromFile:
            file = open(fileName, "r")
            nodes = jsonpickle.decode(file.read())
            file.close()
        else:
            listenSocket = config["listenSocket"]
            broadcastSocket = config["broadcastSocket"]

            cmdAllLedsOn(enable=True)
            cmdWhoAmI(start=True)

            endTime = time.time() + TIME_TO_WAIT

            print("Starting setup process, please wait...")

            while time.time() < endTime:
                try:
                    rawData, _ = listenSocket.recvfrom(1024)
                    data = json.loads(rawData)

                    if "MAC" in data:
                        mac = data["MAC"]
                        ip = data["IP"]

                        if verbose:
                            print("WHO AM I message from MAC", mac, ", IP is ", ip)
                        if mac not in nodes:
                            nodes[mac] = Node(nodeID=mac, ip=ip)
                except KeyboardInterrupt:
                    break
            
            cmdAllLedsOn(enable=False)
            cmdWhoAmI(start=False)

            print(f"\n\nAvailable nodes (%d):" % len(nodes))
            for _, node in nodes.items():
                print("\tMAC: ", node.nodeID, "\tIP: ", node.ip)

            for key, node in nodes.items():
                cmdSingleLedOn(node.ip, enable=True)
                print("")
                print(f"Currently configuring node with MAC address %s and IP address %s" % (node.nodeID, node.ip))
                print("Only this node's high-power LED is currently on, please provide its position below:\n")
                nodes[key].position.x = float(input("\tNode's x-coordinate:\t"))
                nodes[key].position.y = float(input("\tNode's y-coordinate:\t"))
                nodes[key].position.z = float(input("\tNode's z-coordinate:\t"))
                print("\n")

                cmdSingleLedOn(node.ip, enable=False)
            
            file = open("config.txt", "w") 
            file.write(jsonpickle.encode(nodes))
            file.close()

            print("\n\nNode overview:")
            for _, node in nodes.items():
                print("\tMAC: ", node.nodeID, "\tIP: ", node.ip, "\t\tx: ", round(node.position.x, 2), "\ty: ", round(node.position.y, 2), "\tz: ", round(node.position.z), 2)

            print("\nSetup completed\n")

            cmdAllLedsDefault()

        return nodes

    except KeyboardInterrupt:
        cmdAllLedsDefault()
        sys.exit()
    

if __name__ == "__main__":
   main(sys.argv[1:])
