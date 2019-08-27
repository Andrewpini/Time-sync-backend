import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import time



class NodeEntry(QtWidgets.QListWidgetItem):
    COLOR_ACTIVE = QtGui.QBrush(QtGui.QColor("#4278f5"))
    COLOR_UNACTIVE = QtGui.QBrush(QtGui.QColor("#ff1500"))
    def __init__(self, entry):
        super(NodeEntry, self).__init__()
        self.ip_addr = entry.IP
        self.mac_addr = entry.mac
        self.element_addr = entry.element_addr
        self.last_active_timestamp = time.time()
        self.is_active_node = bool
        self.setText(entry.ID_string)
        self.set_active(True)
        self.setData(1, self)

    def update_entry(self):
        self.last_active_timestamp = time.time()
        self.set_active(True)

    def set_active(self, is_active):
        self.is_active_node = is_active
        if is_active:
            self.setForeground(self.COLOR_ACTIVE)
        else:
            self.setForeground(self.COLOR_UNACTIVE)




class NodeList(QtCore.QTimer):
    node_list_timeout_sig = QtCore.pyqtSignal()
    def __init__(self, timeout_val, parent=None):
        super(NodeList, self).__init__(parent)
        self.node_dict = {}
        self.node_cnt = 0

        self.timeout.connect(self.check_for_timeout)
        self.start(timeout_val)

    def add_node(self, node_entry):
        if str(node_entry.mac) in self.node_dict:
            self.node_dict[str(node_entry.mac)].update_entry()
            return None
        else:
            new_node = NodeEntry(node_entry)
            self.node_cnt += 1
            self.node_dict[str(node_entry.mac)] = new_node
            return new_node

    def check_for_timeout(self):
        timestamp = time.time()
        for node_name, node in self.node_dict.items():
            if (timestamp - node.last_active_timestamp) > 5:
                node.set_active(False)
        self.node_list_timeout_sig.emit()