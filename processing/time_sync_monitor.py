import getopt
import socket
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys
import random
import csv
import datetime
import time
from utils import Interval
import sys
import getopt
import socket
import json


class CurveObj:

    def __init__(self, var, inc):
        self.plot_var = var
        self.increment = inc

    buffer = object
    curve = object

    buffer_x = object
    buffer_y = object


def close_app():
    sys.exit()


def add_curve():
    global dummy_counter, LINECOLORS, active_nodes, NODES
    new_curve = CurveObj(0, random.randint(1, 10))
    new_curve.curve = p1.plot(pen=LINECOLORS[dummy_counter], name=NODES[dummy_counter])
    new_curve.buffer_x = list()
    new_curve.buffer_y = list()
    curves.append(new_curve)


def sniff_for_packet():
    global active_nodes, teller
    listenSocket.settimeout(0.05)
    try:
        # Loads the incoming data into a json format
        raw_data, addr = listenSocket.recvfrom(1024)
        print(raw_data)

        if raw_data in active_nodes:
            print('already in there')
            # active_nodes[raw_data]
        else:
            active_nodes[raw_data] = CurveObj(0, random.randint(1, 10))
            active_nodes[raw_data].curve = p1.plot(pen=LINECOLORS[len(active_nodes)], name=str(raw_data))
            active_nodes[raw_data].buffer_x = list()
            active_nodes[raw_data].buffer_y = list()

        teller += 1
        active_nodes[raw_data].buffer_x.append(teller)
        timestamp = random.randint(-5,5)
        active_nodes[raw_data].buffer_y.append(timestamp)

        local_time = datetime.datetime.now()
        local_time = local_time.strftime("%H:%M:%S")

        with open(file_name, 'a', newline='') as csvfile:
            fieldnames = ["Local_time", 'Event_ID', 'Node', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            thisdict = {"Local_time": local_time, "Event_ID": teller, "Node": str(raw_data), "Timestamp": timestamp}
            print(thisdict)
            writer.writerow(thisdict)
            csvfile.close()

        active_nodes[raw_data].curve.setData(active_nodes[raw_data].buffer_x, active_nodes[raw_data].buffer_y)
        app.processEvents()

    except socket.timeout:
        a = 0


def foo():
    print("This is a button")


def main(argv):
    opts, args = getopt.getopt(argv, "cghilt:o", ["ip=", "broadcast_mode"])

    if len(opts) == 0:
        print("time_sync_monitor.py -i <server IP address>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("time_sync_monitor.py -i <server IP address>")
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
            print(ip)
        elif opt in ("-b", "--broadcast_mode"):
            print("Running time_sync_monitor.py in broadcast mode")
        else:
            print("time_sync_monitor.py -i <server IP address> or time_sync_monitor.py -b")
            sys.exit(2)

####################################################################################################

now = datetime.datetime.now()
file_name = "raw_sync_data_" + now.strftime("%d-%m-%Y(%H_%M)") + ".csv"

with open(file_name, 'w', newline='') as csvfile:
    fieldnames = ["Local_time", 'Event_ID', 'Node', 'Timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    csvfile.close()

LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'w']
NODES = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf']
active_nodes = dict()
curves = list()

size = 100
buffersize = 2*100
x = 0
teller = 0

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11001

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))

if not QtGui.QApplication.instance():
    app = QtGui.QApplication([])
else:
    app = QtGui.QApplication.instance()

win = QtGui.QWidget()
win.setWindowTitle("Time sync plot")
win.resize(1000, 600)
layout = QtGui.QGridLayout()
win.setLayout(layout)

b1 = QtGui.QPushButton("Add graph")
b1.clicked.connect(add_curve)

b2 = QtGui.QPushButton("Close")
b2.clicked.connect(close_app)

p1 = pg.PlotWidget()
p1.setRange(yRange=[0, 1000000])
p1.addLegend()
p1.showGrid(x=True, y=True, alpha=0.8)
p1.setLabel('left', 'Amplitude (16bit Signed)')

layout.addWidget(p1, 0, 0, 1, 3)
layout.addWidget(b1, 1, 0)
layout.addWidget(b2, 1, 2)

def update():
    global x, size, buffersize
    x += 1
    for curve in curves:
        k = curve.buffer[buffersize]
        curve.buffer[k] = curve.buffer[k + size] = curve.plot_var
        curve.plot_var = curve.plot_var + random.randint(-5, 5)
        curve.buffer[buffersize] = k = (k + 1) % size
        curve.curve.setData(curve.buffer[k:k + size])
        curve.curve.setPos(x, 0)
    app.processEvents()


timer = QtCore.QTimer()
timer.timeout.connect(sniff_for_packet)
timer.start(25)
timer.setInterval(25)

timer_x = QtCore.QTimer()
timer_x.timeout.connect(update)
timer_x.start(1000)
timer_x.setInterval(1000)

win.show()
app.exec_()

if __name__ == "__main__":
    main(sys.argv[1:])



