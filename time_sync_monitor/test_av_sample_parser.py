import sys
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
import time
from test_render_plot import *
import random
import pandas as pd



class RawSample:
    def __init__(self, event_nr, node, timestamp):
        self.event_nr = event_nr
        self.node = node
        self.timestamp = timestamp



class SampleCluster:
    UINT32T_MAX = 0xFFFFFFFF
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


    def create_plot_data(self, sync_master):
        node_sample_dict = {}
        for entry in self.cluster_list:
            node_sample_dict[entry.node] = entry.timestamp
        is_status_ok, adjusted_dict = self.adjust_sample_data(node_sample_dict, sync_master)
        return is_status_ok, self.event_nr, adjusted_dict

    def create_csv_data(self):
        csv_dict = {'Sample #': self.event_nr, 'RT Clock': self.local_time, 'Max timestamp delta in microseconds': self.find_max_time_diff()}
        for entry in self.cluster_list:
            csv_dict.update({entry.node: entry.timestamp})
        return csv_dict

    @staticmethod
    def adjust_sample_data(data, sync_master):
        is_status_ok = True
        if sync_master in data:
            offset = data[sync_master]
            for node_name, value in data.items():
                data[node_name] -= offset
                if data[node_name] > SampleCluster.UINT32T_MAX / 2:
                    data[node_name] = -(SampleCluster.UINT32T_MAX - data[node_name])
            return is_status_ok, data
        else:
            is_status_ok = False
            return is_status_ok, None


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
        self.current_sync_master = None


        self.df = pd.DataFrame({'Sample #': [], 'RT Clock': [], 'Max timestamp delta in microseconds': []})

        self.timeout.connect(self.check_for_timeout)
        self.start(3000)

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
        try:
            is_status_ok, sample_nr, timestamp_dict = self.entry_dict[key].create_plot_data(self.current_sync_master)
            print(timestamp_dict)
            if is_status_ok:
                self.plot_signal.emit(sample_nr, timestamp_dict)
        except:
            print('Pushing of sample cluster failed')
        # TODO: Fix the writing to file
        # entry = self.entry_dict[key].create_csv_data()
        # self.df = self.df.append(entry, ignore_index=True)
        # self.df.to_csv('csvdata.csv')
        pass


    def remove_cluster(self, key):
        del self.entry_dict[key]

    def check_for_timeout(self):
        time_now = SampleCluster.add_timestamp()
        keys_to_remove = []
        for key, entry in self.entry_dict.items():
            time_since_creation = time_now - entry.timestamp
            if time_since_creation > self.timeout_in_sec:
                print('Reached timeout for the cluster. Pushed to file (Commented out)')
                keys_to_remove.append(key)
        for key in keys_to_remove:
            self.push_cluster(key)
            self.remove_cluster(key)



    def change_sync_master(self, new_sync_master):
        self.current_sync_master = new_sync_master
