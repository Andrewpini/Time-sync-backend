
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import csv
import datetime
import sys
import getopt
import socket
import json
import random
import pandas as pd
import os
from struct import *
from test_av_sample_parser import *


class CurveObj:

    curve = object
    buffer_x = object
    buffer_y = object


def print_plot_data(nr, dicti):
    print(nr)
    print(dicti)
    print('kråke')

def refine_sync_data():
    df = pd.read_csv(raw_file_name)

    df_init = {'Sample #': [], 'RT Clock': [], 'Max timestamp delta in microseconds': []}
    df_nice = pd.DataFrame(df_init)

    # Get all unique node names and add a new column for each in the data frame
    nodes = df.Node.unique()
    nodes.sort()
    for node_id in nodes:
        df_nice[node_id] = 'default value'

    # Get all unique samples and assign one row for each in the data frame
    sample_ids = df.Event_ID.unique()
    sample_ids.sort()
    for i in sample_ids:

        y = {'Sample #': i}
        x = df.loc[df['Event_ID'] == i]
        y.update({'RT Clock': x.iloc[0]['Local_time']})

        timestamp_list = []
        timestamp_diff = []

        for j, row in x.iterrows():
            y.update({row.Node: row.Timestamp})
            timestamp_list.append(row.Timestamp)

        for j in timestamp_list:
            for k in timestamp_list:
                diff = abs(j - k)
                if diff > TIMER_MAX_VAL / 2:
                    diff = TIMER_MAX_VAL - diff
                timestamp_diff.append(diff)

        y.update({'Max timestamp delta in microseconds': max(timestamp_diff)})
        df_nice = df_nice.append(y, ignore_index=True)

    df_nice['Sample #'] = df_nice['Sample #'].astype(int)
    df_nice['Max timestamp delta in microseconds'] = df_nice['Max timestamp delta in microseconds'].astype(int)

    df_nice.to_csv(refined_file_name)


def close_app():
    refine_sync_data()
    sys.exit()


def create_semi_random_color(low_limit, high_limit, alpha):
    color_tuple = (low_limit, high_limit, random.randint(low_limit, high_limit))
    color_tuple = random.sample(color_tuple, len(color_tuple))
    color_tuple += (alpha,)
    return color_tuple


def sniff_for_packet():
    global active_nodes, raw_file_name
    listenSocket.settimeout(0.05)
    try:
        # Loads the incoming data into a json format
        raw_data, addr = listenSocket.recvfrom(1024)
        # print(raw_data)
        data = unpack_from('=IB6sII', raw_data, 0)
        #'=Ib6sII'
        # print(data)
        raw_data_packet = RawSample(data[3], addr[0], data[4])
        parser.add_sample(raw_data_packet)
        # data = json.loads(raw_data)
        ip = addr[0]

        # Gets the computer clock for the moment the data sample is recived
        # and adds it to the raw .csv-file
        local_time = datetime.datetime.now()
        local_time = local_time.strftime("%H:%M:%S")

        # event_id = data['timetic']
        # timestamp = data['drift']
        event_id = data[3]
        timestamp = data[4]

        if ip in active_nodes:
            # print('already in there')
            pass
        else:
            active_nodes[ip] = CurveObj()
            active_nodes[ip].curve = p1.plot(pen=create_semi_random_color(94, 255, 255), name=ip)
            active_nodes[ip].buffer_x = list()
            active_nodes[ip].buffer_y = list()

        active_nodes[ip].buffer_x.append(event_id)
        active_nodes[ip].buffer_y.append(timestamp % TIMER_MAX_VAL)

        with open(raw_file_name, 'a', newline='') as csvfile:
            fieldnames = ["Local_time", 'Event_ID', 'Node', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            thisdict = {"Local_time": local_time, "Event_ID": event_id, "Node": ip, "Timestamp": timestamp}
            # print(thisdict)
            writer.writerow(thisdict)
            csvfile.close()

        active_nodes[ip].curve.setData(active_nodes[ip].buffer_x, active_nodes[ip].buffer_y)
        app.processEvents()

    except socket.timeout:
        pass


def create_file_names(raw_dir, refined_dir):
    now = datetime.datetime.now()
    raw = raw_dir + now.strftime("%d-%m-%Y(%H-%M)") + ".csv"
    refined = refined_dir + now.strftime("%d-%m-%Y(%H-%M)") + ".csv"
    return raw, refined


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


LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 11003
TIMER_MAX_VAL = 1000000
RAW_DATA_DIR_NAME = "./raw_data_sets/"
REFINED_DATA_DIR_NAME = "./refined_data_sets/"
active_nodes = dict()

# Create directories and file names
os.makedirs(RAW_DATA_DIR_NAME, exist_ok=True)
os.makedirs(REFINED_DATA_DIR_NAME, exist_ok=True)
raw_file_name, refined_file_name = create_file_names(RAW_DATA_DIR_NAME, REFINED_DATA_DIR_NAME)

with open(raw_file_name, 'w', newline='') as csvfile:
    fieldnames = ["Local_time", 'Event_ID', 'Node', 'Timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    csvfile.close()


listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))


# Checks if there already is an existing instance running
if not QtGui.QApplication.instance():
    app = QtGui.QApplication([])
else:
    app = QtGui.QApplication.instance()

win = QtGui.QWidget()
win.setWindowTitle("Time sync plot")
win.resize(1000, 600)
layout = QtGui.QGridLayout()
win.setLayout(layout)

b2 = QtGui.QPushButton("End sampling")
b2.clicked.connect(close_app)

p1 = pg.PlotWidget()
p1.setYRange(0, TIMER_MAX_VAL)
p1.addLegend()
p1.showGrid(x=True, y=True, alpha=0.8)

layout.addWidget(p1, 0, 0, 1, 3)
layout.addWidget(b2, 1, 2)

timer = QtCore.QTimer()
timer.timeout.connect(sniff_for_packet)
timer.start(25)
timer.setInterval(25)

#TODO: Remove after testing
parser = SampleParser(8, 1)
parser.plot_signal.connect(print_plot_data)
win.show()

app.exec_()

if __name__ == "__main__":
    main(sys.argv[1:])



