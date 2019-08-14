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


class Ui_main_widget(object):

    def __init__(self, main_widget):
        self.node_list = dict()
        self.node_count = 0
        self.selected_item = str()
        self.active_node_color = QtGui.QBrush(QtGui.QColor("#4278f5"))
        self.unactive_node_color = QtGui.QBrush(QtGui.QColor("#ff1500"))
        self.cpw = ctrlpanelwidget.CtrlPanelWidget(main_widget)
        self.connect_widgets()
        self.ethernet = ethernetcomm.EthernetCommunicationThread("0.0.0.0", 11001, "255.255.255.255", 10000)
        self.ethernet.incoming_ethernet_data_sig.connect(self.add_node)

    def connect_widgets(self):
        self.cpw.list_of_nodes.currentItemChanged.connect(self.on_item_changed)
        self.cpw.time_sync_start_btn.clicked.connect(lambda: self.send_btn_msg(('Time Sync Start').encode()))
        self.cpw.time_sync_stop_btn.clicked.connect(lambda: self.send_btn_msg(('Time Sync Stop').encode()))
        self.cpw.sync_line_start_btn.clicked.connect(lambda: self.send_btn_msg(('Sync Start Start').encode()))
        self.cpw.sync_line_stop_btn.clicked.connect(lambda: self.send_btn_msg(('Sync Line Stop').encode()))

    def add_node(self, unicast, ip, mac):
        list_ID = str('IP: ' + ip + ' | ' + 'MAC: ' + mac + ' | ' + 'Unicast: ' + unicast)
        if list_ID in self.node_list:
            self.node_list[list_ID]['last_timestamp'] = time.time()
            self.node_list[list_ID]['is_active'] = True
            self.node_list[list_ID]['list_item'].setForeground(self.active_node_color)
            if self.selected_item == list_ID:
                self.cpw.is_init_frame.setEnabled(True)
        else:
            list_item = QtWidgets.QListWidgetItem(list_ID)
            list_item.setForeground(self.active_node_color)
            self.node_list[list_ID] = {'ip': ip, 'Mac': mac, 'Uni': unicast, 'last_timestamp': time.time(), 'list_item': list_item, 'selector_idx': self.node_count, 'is_active': True}
            self.cpw.list_of_nodes.addItem(self.node_list[list_ID]['list_item'])
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

    def send_btn_msg(self, msg):
        self.ethernet.broadcast_data(msg)
        # print(self.ethernet)
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_widget = QtWidgets.QWidget()
    ui = Ui_main_widget(main_widget)

    timer = QtCore.QTimer()
    timer.timeout.connect(ui.node_timeout_check)
    timer.start(5000)

    main_widget.show()
    sys.exit(app.exec_())

