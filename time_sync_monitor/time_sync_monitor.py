
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import csv
import datetime
import sys
import getopt
import socket
import json
import os
from src import curve_plot
import pandas as pd


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
    # refine_dataset.refine_sync_data(raw_file_name, refined_file_name, TIMER_MAX_VAL)
    refine_sync_data()
    sys.exit()


def incoming_packet_handler():
    global active_nodes, raw_file_name, x
    listenSocket.settimeout(0.05)

    try:
        # Loads the incoming data into a json format
        raw_data, addr = listenSocket.recvfrom(1024)
        data = json.loads(raw_data)
        ip = addr[0]
        event_id = data['timetic']
        timestamp = data['drift']

        # # Add the incoming sample to the plot
        if ip not in active_nodes:
            active_nodes[ip] = curve_plot.add_new_curve(pl, ip)
        active_nodes[ip].add_single_sample(event_id, timestamp % TIMER_MAX_VAL)
        active_nodes[ip].curve.setData(active_nodes[ip].buffer_x, active_nodes[ip].buffer_y)

        # Gets the computer clock for the moment the data sample is recived
        # and adds it to the raw .csv-file
        local_time = datetime.datetime.now()
        local_time = local_time.strftime("%H:%M:%S")

        with open(raw_file_name, 'a', newline='') as csvfile:
            fieldnames = ["Local_time", 'Event_ID', 'Node', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            this_dict = {"Local_time": local_time, "Event_ID": event_id, "Node": ip, "Timestamp": timestamp}
            writer.writerow(this_dict)
            csvfile.close()

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
LISTEN_PORT = 11001
TIMER_MAX_VAL = 1000000
RAW_DATA_DIR_NAME = "./raw_data_sets/"
REFINED_DATA_DIR_NAME = "./refined_data_sets/"
active_nodes = dict()

# Create directories and file names
os.makedirs(RAW_DATA_DIR_NAME, exist_ok=True)
os.makedirs(REFINED_DATA_DIR_NAME, exist_ok=True)
raw_file_name, refined_file_name = create_file_names(RAW_DATA_DIR_NAME, REFINED_DATA_DIR_NAME)

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listenSocket.bind((LISTEN_IP, LISTEN_PORT))

local_time = datetime.datetime.now()
local_time = local_time.strftime("%H:%M:%S")

with open(raw_file_name, 'w', newline='') as csvfile:
    fieldnames = ["Local_time", 'Event_ID', 'Node', 'Timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    csvfile.close()

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

pl = pg.PlotWidget()
pl.setYRange(0, TIMER_MAX_VAL)
pl.addLegend()
pl.showGrid(x=True, y=True, alpha=0.8)

layout.addWidget(pl, 0, 0, 1, 3)
layout.addWidget(b2, 1, 2)

test = curve_plot.add_new_curve(pl, 'pøls')
test.add_multiple_samples([1,2,3,4,5],[1,2,3,4,5])
test.add_single_sample(6,6)
test.curve.setData(test.buffer_x, test.buffer_y)

timer = QtCore.QTimer()
timer.timeout.connect(incoming_packet_handler)
timer.start(25)
timer.setInterval(25)

win.show()

app.exec_()

if __name__ == "__main__":
    main(sys.argv[1:])



