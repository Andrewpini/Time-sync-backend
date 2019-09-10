
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
        self.selected_item = NodeEntry
        self.current_time_sync_node = 'None'
        self.current_sync_line_node = 'None'
        self.node_list = NodeList(1000)
        # TODO: Dynamicaly update node cnt
        self.parser = SampleParser(8, 2)
        self.cpw = ctrlpanelwidget.CtrlPanelWidget(main_widget)
        self.connect_widgets()
        self.cpw.plot_sample_label.setText('Samples shown: %d' % self.cpw.horizontalSlider.value())

        # Create ethernet communication instance and connect signals to corresponding handlers
        self.ethernet = ethernetcomm.EthernetCommunicationThread("0.0.0.0", 11001, "255.255.255.255", 10000)

        self.ethernet.sig_i_am_alive.connect(self.i_am_alive_msg_handler)
        self.ethernet.sig_ack_msg.connect(self.ack_msg_handler)
        # self.ethernet.sig_sync_line_sample_msg.connect(self.handle_time_sync_sample)
        self.node_list.node_list_timeout_sig.connect(self.node_list_timeout_handler)
        self.parser.plot_signal.connect(self.handle_parser_output)



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
        self.cpw.dfu_single_btn.clicked.connect(lambda: self.send_dfu_msg(False, self.selected_item.mac_addr))
        self.cpw.dfu_all_btn.clicked.connect(lambda: self.send_dfu_msg(True, None))
        self.cpw.reset_btn.clicked.connect(lambda: self.send_reset_msg(False, self.selected_item.mac_addr))
        self.cpw.reset_all_btn.clicked.connect(lambda: self.send_reset_msg(True, None))
        self.cpw.tx_pwr_btn.clicked.connect(lambda: self.send_tx_pwr_msg(False, self.selected_item.mac_addr))
        self.cpw.tx_pwr_all_btn.clicked.connect(lambda: self.send_tx_pwr_msg(True, None))
        # self.cpw.tx_pwr_all_btn.clicked.connect(self.cpw.plot1.clear_entire_plot)
        self.cpw.horizontalSlider.valueChanged.connect(lambda: self.cpw.plot2.set_partial_sampleset_cnt(self.cpw.horizontalSlider.value()))
        self.cpw.horizontalSlider.valueChanged.connect(lambda: self.cpw.plot_sample_label.setText('Samples shown: %d' % self.cpw.horizontalSlider.value()))
        self.cpw.clear_plot_btn.clicked.connect(self.handle_clear_plot)

    def i_am_alive_msg_handler(self, msg):
        new = self.node_list.add_node(msg)
        if new is not None:
            self.cpw.list_of_nodes.addItem(new)

    def on_item_changed(self, curr, prev):

        self.selected_item = curr.data(1)
        self.cpw.list_of_nodes.setCurrentItem(curr)
        if self.selected_item.is_active_node:
            self.cpw.set_clickable_widgets(True)
        else:
            self.cpw.set_clickable_widgets(False)

    def send_sync_line_start_msg(self):
        msg = StartSyncLineMsg().get_packed_msg(self.selected_item.mac_addr)
        self.ethernet.broadcast_data(msg)
        self.cpw.sync_line_label.setText('Starting - Waiting for response from node %s' % self.selected_item.ip_addr)
        self.current_sync_line_node = self.selected_item.ip_addr

        # Set new sync master for the parser
        self.parser.change_sync_master(str(self.selected_item.mac_addr))

        # Reset the plot if a new sync line master msg, I. e. the user starts a new session
        self.cpw.plot1.reset_plotter()
        self.cpw.plot2.reset_plotter()
        self.cpw.plot1.clear_entire_plot()
        self.cpw.plot2.clear_entire_plot()

    def send_sync_line_stop_msg(self):
        msg = StopSyncLineMsg().get_packed_msg(self.selected_item.mac_addr)
        self.ethernet.broadcast_data(msg)
        self.cpw.sync_line_label.setText('Stopping - Waiting for response from node %s' % self.current_sync_line_node)


    def send_time_sync_start_msg(self):
        msg = StartTimeSyncMsg().get_packed_msg(self.selected_item.mac_addr)
        self.ethernet.broadcast_data(msg)
        self.cpw.time_sync_label.setText('Starting - Waiting for response from node %s' % self.selected_item.ip_addr)
        self.current_time_sync_node = self.selected_item.ip_addr

    def send_time_sync_stop_msg(self):
        msg = StopTimeSyncMsg().get_packed_msg(self.selected_item.mac_addr)
        self.ethernet.broadcast_data(msg)
        self.cpw.time_sync_label.setText('Stopping - Waiting for response from node %s' % self.current_time_sync_node)

    def send_led_msg(self, is_broadcast, on_off, target_addr):
        try:
            ting = LedMsg().get_packed_msg(is_broadcast, on_off, target_addr)
            self.ethernet.broadcast_data(ting)
        except Exception as e:
            print("PENIS 2")
            print(e)


    def send_dfu_msg(self, is_broadcast, target_addr):
        ting = DfuMsg().get_packed_msg(is_broadcast, target_addr)
        self.ethernet.broadcast_data(ting)

    def send_reset_msg(self, is_broadcast, target_addr):
        ting = ResetMsg().get_packed_msg(is_broadcast, target_addr)
        self.cpw.sync_line_label.setText('Reset has been pressed! Behaviour of sync line uncertain...')
        self.cpw.time_sync_label.setText('Reset has been pressed! Behaviour of time sync uncertain...')
        self.ethernet.broadcast_data(ting)


    def send_tx_pwr_msg(self, is_broadcast, target_addr):
        ting = TxPowerMsg().get_packed_msg(is_broadcast, self.cpw.tx_power_cbox.currentIndex(), target_addr)
        self.ethernet.broadcast_data(ting)

    def ack_msg_handler(self, msg):
        if msg.ack_opcode == OPCODES['StartSyncLineMsg']:
            self.cpw.sync_line_label.setText('Current sync line master is node %s' % msg.sender_mac_addr)
        if msg.ack_opcode == OPCODES['StopSyncLineMsg']:
            self.cpw.sync_line_label.setText('Sync line was stopped by user')
        if msg.ack_opcode == OPCODES['StartTimeSyncMsg']:
            self.cpw.time_sync_label.setText('Current time sync master is node %s' % msg.sender_mac_addr)
        if msg.ack_opcode == OPCODES['StopTimeSyncMsg']:
            self.cpw.time_sync_label.setText('Time sync was stopped by user')

    def handle_time_sync_sample(self, msg):
        if self.parser.current_sync_master is not None:
            self.parser.add_sample(RawSample(msg.sample_nr, str(msg.mac), msg.sample_val))
        else:
            # print('Debug info: Sync master is not set in the parser. Reset all nodes and choose a sync line master')
            pass


    def handle_slider_event(self):
        slider_val = self.cpw.horizontalSlider.value()
        self.cpw.plot2.set_partial_sampleset_cnt(slider_val)
        self.cpw.plot_sample_label.setText('Samples shown: %d' % slider_val)

    def node_list_timeout_handler(self):
        try:
            if self.selected_item.is_active_node:
                self.cpw.set_clickable_widgets(True)
            else:
                self.cpw.set_clickable_widgets(False)
        except:
            pass

    def handle_clear_plot(self):
        self.cpw.plot1.clear_entire_plot()
        self.cpw.plot2.clear_entire_plot()


    def handle_parser_output(self, nr, dicti):
        self.cpw.plot1.add_plot_sample(nr, dicti)
        self.cpw.plot2.add_plot_sample(nr, dicti)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_widget = QtWidgets.QMainWindow()
    ui = Ui_main_widget(main_widget)




    main_widget.show()
    sys.exit(app.exec_())

