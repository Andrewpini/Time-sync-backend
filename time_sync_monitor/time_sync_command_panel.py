
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import time
import ethernetcomm
import ctrlpanelwidget
from ethernetmsg import *
import struct
import random
from test_av_sample_parser import *
from node_list import *

def create_random_TID():
    UINT32_MAX = 0xffffffff
    random.seed(time.time())
    return random.randint(0, UINT32_MAX)

class Ui_main_widget(object):

    def __init__(self, main_widget):
        self.node_list = dict()
        self.node_count = 0
        self.selected_item = NodeEntry
        self.current_time_sync_node = 'None'
        self.current_sync_line_node = 'None'
        self.active_node_color = QtGui.QBrush(QtGui.QColor("#4278f5"))
        self.unactive_node_color = QtGui.QBrush(QtGui.QColor("#ff1500"))
        self.current_TID = None
        self.tras = NodeList(1000)

        self.cpw = ctrlpanelwidget.CtrlPanelWidget(main_widget)
        self.connect_widgets()
        self.cpw.plot_sample_label.setText('Samples shown: %d' % self.cpw.horizontalSlider.value())

        # Create ethernet communication instance and connect signals to corresponding handlers
        self.ethernet = ethernetcomm.EthernetCommunicationThread("0.0.0.0", 11001, "255.255.255.255", 10000)

        self.ethernet.sig_i_am_alive.connect(self.add_node)

        self.ethernet.sig_ack_msg.connect(self.handle_ack_msg)
        self.ethernet.sig_sync_line_sample_msg.connect(self.handle_time_sync_sample)



    def connect_widgets(self):
        self.cpw.list_of_nodes.currentItemChanged.connect(self.on_item_changed)
        self.cpw.time_sync_start_btn.clicked.connect(self.send_time_sync_start_msg)
        self.cpw.time_sync_stop_btn.clicked.connect(self.send_time_sync_stop_msg)
        self.cpw.sync_line_start_btn.clicked.connect(self.send_sync_line_start_msg)
        self.cpw.sync_line_stop_btn.clicked.connect(self.send_sync_line_stop_msg)
        self.cpw.led_on_btn.clicked.connect(lambda: self.send_led_msg(False, True, self.selected_item.mac_addr))
        self.cpw.led_off_btn.clicked.connect(lambda: self.send_led_msg(False, False, self.selected_item.mac_addr))
        self.cpw.led_all_on_btn.clicked.connect(lambda: self.send_led_msg(True, True, None))
        self.cpw.led_all_off_btn.clicked.connect(lambda: self.send_led_msg(True, False, None))
        self.cpw.dfu_single_btn.clicked.connect(lambda: self.send_dfu_msg(False, self.node_list[self.selected_item]['Mac']))
        self.cpw.dfu_all_btn.clicked.connect(lambda: self.send_dfu_msg(True, None))
        self.cpw.reset_btn.clicked.connect(lambda: self.send_reset_msg(False, self.node_list[self.selected_item]['Mac']))
        self.cpw.reset_all_btn.clicked.connect(lambda: self.send_reset_msg(True, None))
        self.cpw.tx_pwr_btn.clicked.connect(lambda: self.send_tx_pwr_msg(False, self.node_list[self.selected_item]['Mac']))
        self.cpw.tx_pwr_all_btn.clicked.connect(lambda: self.send_tx_pwr_msg(True, None))
        self.cpw.tx_pwr_all_btn.clicked.connect(self.cpw.plot1.clear_entire_plot)
        self.cpw.horizontalSlider.valueChanged.connect(lambda: self.cpw.plot2.set_partial_sampleset_cnt(self.cpw.horizontalSlider.value()))
        self.cpw.horizontalSlider.valueChanged.connect(lambda: self.cpw.plot_sample_label.setText('Samples shown: %d' % self.cpw.horizontalSlider.value()))

    def add_node(self, msg):
        new = self.tras.add_node(msg)
        if new is not None:
            self.cpw.list_of_nodes.addItem(new)

        # if msg.ID_string in self.node_list:
        #     self.node_list[msg.ID_string]['last_timestamp'] = time.time()
        #     self.node_list[msg.ID_string]['is_active'] = True
        #     self.node_list[msg.ID_string]['list_item'].setForeground(self.active_node_color)
        #     if self.selected_item == msg.ID_string:
        #         self.cpw.set_clickable_widgets(True)
        # else:
        #     list_item = QtWidgets.QListWidgetItem()
        #     list_item.setText(msg.ID_string)
        #     list_item.setForeground(self.active_node_color)
        #     self.node_list[msg.ID_string] = {'ip': msg.IP, 'Mac': msg.mac, 'Uni': 0, 'last_timestamp': time.time(), 'list_item': list_item, 'selector_idx': self.node_count, 'is_active': True}
        #     self.cpw.list_of_nodes.addItem(self.node_list[msg.ID_string]['list_item'])
        #     self.node_count += 1

    def node_timeout_check(self):
        timestamp = time.time()
        # for node_ip in self.node_list:
        #     if (timestamp - self.node_list[node_ip]['last_timestamp']) > 5:
        #         self.node_list[node_ip]['list_item'].setForeground(self.unactive_node_color)
        #         self.node_list[node_ip]['is_active'] = False
        #         if self.selected_item == node_ip:
        #             self.cpw.set_clickable_widgets(False)

    def on_item_changed(self, curr, prev):
        # self.selected_item = curr.text()
        # # print(self.cpw.list_of_nodes.currentRow())
        # self.cpw.list_of_nodes.setCurrentItem(self.node_list[self.selected_item]['list_item'])
        # if self.node_list[self.selected_item]['is_active']:
        #     self.cpw.set_clickable_widgets(True)
        # else:
        #     self.cpw.set_clickable_widgets(False)
        self.selected_item = curr.data(1)
        # print(self.cpw.list_of_nodes.currentRow())
        self.cpw.list_of_nodes.setCurrentItem(curr)
        if self.selected_item.is_active_node:
            self.cpw.set_clickable_widgets(True)
        else:
            self.cpw.set_clickable_widgets(False)

    def send_sync_line_start_msg(self):
        self.current_TID = create_random_TID()
        print(self.selected_item.mac_addr)
        ting = StartSyncLineMsg().get_packed_msg(self.selected_item.mac_addr, self.current_TID)
        self.ethernet.broadcast_data(ting)
        # self.cpw.sync_line_label.setText('Starting - Waiting for response from node %s' % self.node_list[self.selected_item]['ip'])
        # self.current_sync_line_node = self.node_list[self.selected_item]['ip']

    def send_sync_line_stop_msg(self):
        self.current_TID = create_random_TID()
        print(self.node_list[self.selected_item]['Mac'])

        ting = StopSyncLineMsg().get_packed_msg(self.node_list[self.selected_item]['Mac'], self.current_TID)
        self.ethernet.broadcast_data(ting)
        self.cpw.sync_line_label.setText('Stopping - Waiting for response from node %s' % self.current_sync_line_node)

    def send_time_sync_start_msg(self):
        self.current_TID = create_random_TID()
        ting = StartTimeSyncMsg().get_packed_msg(self.node_list[self.selected_item]['Mac'], self.current_TID)
        self.ethernet.broadcast_data(ting)
        self.cpw.time_sync_label.setText('Starting - Waiting for response from node %s' % self.node_list[self.selected_item]['ip'])
        self.current_time_sync_node = self.node_list[self.selected_item]['ip']

    def send_time_sync_stop_msg(self):
        self.current_TID = create_random_TID()
        ting = StopTimeSyncMsg().get_packed_msg(self.node_list[self.selected_item]['Mac'], self.current_TID)
        self.ethernet.broadcast_data(ting)
        self.cpw.time_sync_label.setText('Stopping - Waiting for response from node %s' % self.current_time_sync_node)

    def send_led_msg(self, is_broadcast, on_off, target_addr):
        ting = LedMsg().get_packed_msg(is_broadcast, on_off, target_addr)
        self.ethernet.broadcast_data(ting)

    def send_dfu_msg(self, is_broadcast, target_addr):
        ting = DfuMsg().get_packed_msg(is_broadcast, target_addr)
        self.ethernet.broadcast_data(ting)

    def send_reset_msg(self, is_broadcast, target_addr):
        ting = ResetMsg().get_packed_msg(is_broadcast, target_addr)
        self.ethernet.broadcast_data(ting)

    def send_tx_pwr_msg(self, is_broadcast, target_addr):
        ting = TxPowerMsg().get_packed_msg(is_broadcast, self.cpw.tx_power_cbox.currentIndex(), target_addr)
        self.ethernet.broadcast_data(ting)

    def handle_ack_msg(self, msg):
        if self.current_TID == msg.TID:
            if msg.ack_opcode == OPCODES['StartSyncLineMsg']:
                self.cpw.sync_line_label.setText('Current sync line master is node %s' % msg.sender_mac_addr)
            if msg.ack_opcode == OPCODES['StopSyncLineMsg']:
                self.cpw.sync_line_label.setText('Sync line was stopped by user')
            if msg.ack_opcode == OPCODES['StartTimeSyncMsg']:
                self.cpw.time_sync_label.setText('Current time sync master is node %s' % msg.sender_mac_addr)
            if msg.ack_opcode == OPCODES['StopTimeSyncMsg']:
                self.cpw.time_sync_label.setText('Sync line was stopped by user')
        pass


    def handle_time_sync_sample(self, msg):
        parser.add_sample(RawSample(msg.sample_nr, str(msg.mac), msg.sample_val))


    def handle_slider_event(self):
        slider_val = self.cpw.horizontalSlider.value()
        self.cpw.plot2.set_partial_sampleset_cnt(slider_val)
        self.cpw.plot_sample_label.setText('Samples shown: %d' % slider_val)


def handle_parser_output(nr, dicti):
    ui.cpw.plot1.add_plot_sample(nr, dicti)
    ui.cpw.plot2.add_plot_sample(nr, dicti)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_widget = QtWidgets.QMainWindow()
    ui = Ui_main_widget(main_widget)

    parser = SampleParser(8, 3)
    parser.plot_signal.connect(handle_parser_output)
    ui.cpw.plot1.change_sync_master('B0-73-4A-9E-AA-57')
    ui.cpw.plot2.change_sync_master('B0-73-4A-9E-AA-57')

    timer = QtCore.QTimer()
    timer.timeout.connect(ui.node_timeout_check)
    timer.start(1000)

    main_widget.show()
    sys.exit(app.exec_())

