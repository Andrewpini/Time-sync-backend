import sys
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
import time
from test_render_plot import *
import random


class RawSample:
    def __init__(self, event_nr, node, timestamp):
        self.event_nr = event_nr
        self.node = node
        self.timestamp = timestamp



class SampleCluster:
    UINT32MAX = 4294967295
    def __init__(self, event_nr):
        self.event_nr = event_nr
        self.cluster_list = []
        self.entry_cnt = 0
        self.timestamp = self.add_timestamp()
        self.local_time = self.add_local_time()

    def add_sample_to_cluster(self, sample):
        self.entry_cnt += 1
        self.cluster_list.append(sample)


    def find_max_time_diff(self):
        timestamp_diff = []
        for j in self.cluster_list:
            for k in self.cluster_list:
                diff = abs(j.timestamp - k.timestamp)
                if diff > self.UINT32MAX / 2:
                    diff = self.UINT32MAX - diff
                timestamp_diff.append(diff)
        return max(timestamp_diff)


    def create_plot_data(self):
        node_sample_dict = {}
        for entry in self.cluster_list:
            node_sample_dict[entry.node] = entry.timestamp
        return [self.event_nr, node_sample_dict]

    @staticmethod
    def add_timestamp():
        return time.time()

    @staticmethod
    def add_local_time():
        local_time = datetime.datetime.now()
        return local_time.strftime("%H:%M:%S")





class SampleParser(QtCore.QTimer):
    plot_signal = QtCore.pyqtSignal(int, dict)
    def __init__(self, push_cnt_limit, timeout_in_sec, parent=None):
        super(SampleParser, self).__init__(parent)
        self.entry_dict = {}
        self.push_cnt_limit = push_cnt_limit
        self.timeout_in_sec = timeout_in_sec

        self.timeout.connect(self.check_for_timeout)
        self.start(1000)

    def add_sample(self, sample): # RawSampel class
        if sample.event_nr in self.entry_dict:
            # Adds a sample to a existing cluster
            self.entry_dict[sample.event_nr].add_sample_to_cluster(sample)
            # print('Existing sample')
        else:
            # Appends a new cluster to the entry dict
            new_cluster = SampleCluster(sample.event_nr)
            self.entry_dict[sample.event_nr] = new_cluster
            self.entry_dict[sample.event_nr].add_sample_to_cluster(sample)
            # print('New sample')

        if self.entry_dict[sample.event_nr].entry_cnt == self.push_cnt_limit:
            self.push_cluster(sample.event_nr)
            self.remove_cluster(sample.event_nr)
            print('Reached entry limit for the cluster. Pushed to file')

    def push_cluster(self, key):
        sample_nr, timestamp_dict = self.entry_dict[key].create_plot_data()
        #print(sample_nr)
        #print(timestamp_dict)
        self.plot_signal.emit(sample_nr, timestamp_dict)



    def remove_cluster(self, key):
        del self.entry_dict[key]

    def check_for_timeout(self):
        time_now = SampleCluster.add_timestamp()
        keys_to_remove = []
        for key, entry in self.entry_dict.items():
            time_since_creation = time_now - entry.timestamp
            if time_since_creation > self.timeout_in_sec:
                print('Reached timeout for the cluster. Pushed to file')
                keys_to_remove.append(key)
        for key in keys_to_remove:
            self.push_cluster(key)
            self.remove_cluster(key)


def foo(nr, dicti):
    plotter.add_plot_sample(nr, dicti)
    printer.add_plot_sample(nr, dicti)

def fuu():
    global teller
    parser.add_sample(RawSample(teller, 'gris', random.randint(0,40)))
    parser.add_sample(RawSample(teller, 'høne', random.randint(0,40)))
    parser.add_sample(RawSample(teller, 'hane', random.randint(0,40)))
    parser.add_sample(RawSample(teller, 'trost', random.randint(0,40)))
    parser.add_sample(RawSample(teller, 'trane', random.randint(0,40)))
    parser.add_sample(RawSample(teller, 'lama', random.randint(0,40)))
    parser.add_sample(RawSample(teller, 'kenguru', random.randint(0,40)))
    parser.add_sample(RawSample(teller, 'dingo', random.randint(0,40)))
    teller +=1

if __name__ == "__main__":
    teller = 0

    app = QtWidgets.QApplication(sys.argv)

    parser = SampleParser(8, 3)
    parser.plot_signal.connect(foo)

    win = QtGui.QWidget()
    win.setWindowTitle("Time sync plot")
    win.resize(1000, 600)
    layout = QtWidgets.QVBoxLayout()
    win.setLayout(layout)
    plotter = TimeSyncPlot()
    printer = TimeSyncPlot(plot_partial=True)
    printer.change_sync_master('gris')
    plotter.change_sync_master('gris')


    layout.addWidget(plotter)
    layout.addWidget(printer)
    win.show()


    # parser.add_sample(RawSample(3, 'gris', 20))
    # parser.add_sample(RawSample(3, 'høne', 30))
    # parser.add_sample(RawSample(3, 'hane', 40))
    # parser.add_sample(RawSample(3, 'trost', 10))
    # parser.add_sample(RawSample(3, 'trane', 70))
    # parser.add_sample(RawSample(3, 'lama', 55))
    # parser.add_sample(RawSample(3, 'kenguru', 31))
    # parser.add_sample(RawSample(3, 'dingo', 79))
    # parser.add_sample(RawSample(4, 'gris', 20))
    # parser.add_sample(RawSample(4, 'høne', 30))
    # parser.add_sample(RawSample(4, 'hane', 40))
    # parser.add_sample(RawSample(4, 'trost', 10))
    # parser.add_sample(RawSample(4, 'trane', 70))
    # parser.add_sample(RawSample(4, 'lama', 55))
    # parser.add_sample(RawSample(4, 'kenguru', 31))
    # parser.add_sample(RawSample(4, 'dingo', 79))

    timer = QtCore.QTimer()
    timer.timeout.connect(fuu)
    timer.start(500)

    sys.exit(app.exec_())

