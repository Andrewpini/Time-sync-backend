import sys
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
import time


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
        # print(sample_nr)
        # print(timestamp_dict)
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



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    parser = SampleParser(8, 3)

    parser.add_sample(RawSample(3, 'Nasse Node', 0))
    parser.add_sample(RawSample(3, 'Nasse Node', 0))
    parser.add_sample(RawSample(3, 'Nasse Node', 0))
    parser.add_sample(RawSample(3, 'Nasse Node', 0))
    parser.add_sample(RawSample(3, 'Nasse Node', 0))
    parser.add_sample(RawSample(3, 'Nasse Node', 4294967295/2 +2))
    parser.add_sample(RawSample(3, 'Nasse Node', 0))
    parser.add_sample(RawSample(3, 'Nasse Node', 4294967295-1000))

    sys.exit(app.exec_())

