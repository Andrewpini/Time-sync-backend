# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\test.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import time
import ethernetcomm
import ctrlpanelwidget
import ethernetmsg
import struct


class Ui_main_widget(object):

    def __init__(self, main_widget):
        self.node_list = dict()
        self.node_count = 0
        self.selected_item = str()
        self.active_node_color = QtGui.QBrush(QtGui.QColor("#4278f5"))
        self.unactive_node_color = QtGui.QBrush(QtGui.QColor("#ff1500"))
        self.cpw = ctrlpanelwidget.CtrlPanelWidget(main_widget)
        self.connect_widgets()
        self.ethernet = ethernetcomm.EthernetCommunicationThread("0.0.0.0", 11003, "255.255.255.255", 11003)
        self.ethernet.incoming_ethernet_data_sig.connect(self.add_node)
        self.current_time_sync_node = 'None'
        self.current_sync_line_node = 'None'

    def connect_widgets(self):
        self.cpw.list_of_nodes.currentItemChanged.connect(self.on_item_changed)
        self.cpw.time_sync_start_btn.clicked.connect(self.send_time_sync_start_msg)
        self.cpw.time_sync_stop_btn.clicked.connect(self.send_time_sync_stop_msg)
        self.cpw.sync_line_start_btn.clicked.connect(self.send_sync_line_start_msg)
        self.cpw.sync_line_stop_btn.clicked.connect(self.send_sync_line_stop_msg)
        self.cpw.init_btn.clicked.connect(lambda: self.ethernet.broadcast_data(struct.pack('=Ib6s4sh', 0xDEADFACE, -1, bytes([0xB0, 0x95, 0x55, 0x3B, 0x94, 0xA4]), bytes([10, 0, 0, 11]), 0x4)))
        self.cpw.reset_btn.clicked.connect(lambda: self.send_btn_msg('RESET', struct.pack('=Ib6s4sh', 0xDEADFACE, -1, bytes([0xB0, 0x95, 0x55, 0x3B, 0x94, 0xA4]), bytes([10, 2, 0, 20]), 0x4)))


    def add_node(self, msg):
        if msg.ID_string in self.node_list:
            self.node_list[msg.ID_string]['last_timestamp'] = time.time()
            self.node_list[msg.ID_string]['is_active'] = True
            self.node_list[msg.ID_string]['list_item'].setForeground(self.active_node_color)
            if self.selected_item == msg.ID_string:
                self.cpw.is_init_frame.setEnabled(True)
        else:
            list_item = QtWidgets.QListWidgetItem(msg.ID_string)
            list_item.setForeground(self.active_node_color)
            self.node_list[msg.ID_string] = {'ip': msg.IP, 'Mac': msg.mac, 'Uni': 0, 'last_timestamp': time.time(), 'list_item': list_item, 'selector_idx': self.node_count, 'is_active': True}
            self.cpw.list_of_nodes.addItem(self.node_list[msg.ID_string]['list_item'])
            self.node_count += 1

    def node_timeout_check(self):
        timestamp = time.time()
        for node_ip in self.node_list:
            if (timestamp - self.node_list[node_ip]['last_timestamp']) > 5:
                self.node_list[node_ip]['list_item'].setForeground(self.unactive_node_color)
                self.node_list[node_ip]['is_active'] = False
                if self.selected_item == node_ip:
                    self.cpw.is_init_frame.setEnabled(False)

    def on_item_changed(self, curr, prev):
        self.selected_item = curr.text()
        self.cpw.list_of_nodes.setCurrentItem(self.node_list[self.selected_item]['list_item'])
        if self.node_list[self.selected_item]['is_active']:
            self.cpw.is_init_frame.setEnabled(True)
        else:
            self.cpw.is_init_frame.setEnabled(False)

    def send_sync_line_start_msg(self):
        self.ethernet.broadcast_data(struct.pack('=Ib6s4sh', 0xDEADFACE, -1, bytes([0xB0, 0x95, 0x55, 0x3B, 0x94, 0xA4]), bytes([10, 0, 0, 12]), 0x4))
        self.cpw.sync_line_label.setText('Starting - Waiting for response from node %s' % self.node_list[self.selected_item]['ip'])
        self.current_sync_line_node = self.node_list[self.selected_item]['ip']

    def send_sync_line_stop_msg(self):
        self.ethernet.broadcast_data(struct.pack('=Ib6s4sh', 0xDEADFACE, -1, bytes([0xB0, 0x95, 0x55, 0x3B, 0x94, 0xA4]), bytes([10, 0, 0, 12]), 0x4))
        self.cpw.sync_line_label.setText('Stopping - Waiting for response from node %s' % self.current_sync_line_node)


    def send_time_sync_start_msg(self):
        self.ethernet.broadcast_data(struct.pack('=Ib6s4sh', 0xDEADFACE, -1, bytes([0xB0, 0x95, 0x55, 0x3B, 0x94, 0xA4]), bytes([10, 0, 0, 12]), 0x4))
        self.cpw.time_sync_label.setText('Starting - Waiting for response from node %s' % self.node_list[self.selected_item]['ip'])
        self.current_time_sync_node = self.node_list[self.selected_item]['ip']

    def send_time_sync_stop_msg(self):
        self.ethernet.broadcast_data(struct.pack('=Ib6s4sh', 0xDEADFACE, -1, bytes([0xB0, 0x95, 0x55, 0x3B, 0x94, 0xA4]), bytes([10, 0, 0, 12]), 0x4))
        self.cpw.time_sync_label.setText('Stopping - Waiting for response from node %s' % self.current_time_sync_node)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_widget = QtWidgets.QWidget()
    ui = Ui_main_widget(main_widget)

    timer = QtCore.QTimer()
    timer.timeout.connect(ui.node_timeout_check)
    timer.start(5000)

    main_widget.show()
    sys.exit(app.exec_())

