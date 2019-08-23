from PyQt5 import QtCore, QtGui, QtWidgets
import socket
from ethernetmsg import *


class EthernetCommunicationThread(QtCore.QThread):

    sig_i_am_alive = QtCore.pyqtSignal(object)
    sig_start_sync_line = QtCore.pyqtSignal(object)
    sig_stop_sync_line = QtCore.pyqtSignal(object)
    sig_start_time_sync = QtCore.pyqtSignal(object)
    sig_stop_time_sync = QtCore.pyqtSignal(object)
    sig_reset_msg = QtCore.pyqtSignal(object)
    sig_ack_msg = QtCore.pyqtSignal(object)
    sig_led_msg = QtCore.pyqtSignal(object)
    sig_dfu_msg = QtCore.pyqtSignal(object)
    sig_tx_power_msg = QtCore.pyqtSignal(object)

    def __init__(self, listen_ip, listen_port, broadcast_ip, broadcast_port, parent=None):
        super(EthernetCommunicationThread, self).__init__(parent)
        self.reciver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reciver_sock.bind((listen_ip, listen_port))

        self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.broadcast_ip = broadcast_ip
        self.broadcast_port = broadcast_port
        self.handlers = {
            'IAmAlive': {'type': IAmAliveMsg, 'handler': self.handle_iamalive},
            'StartSyncLine': {'type': StartSyncLineMsg, 'handler': self.handle_start_sync_line},
            'StopSyncLine': {'type': StopSyncLineMsg, 'handler': self.handle_stop_sync_line},
            'StartTimeSync': {'type': StartTimeSyncMsg, 'handler': self.handle_start_time_sync},
            'StopTimeSync': {'type': StopTimeSyncMsg, 'handler': self.handle_stop_time_sync},
            'ResetMsg': {'type': ResetMsg, 'handler': self.handle_reset_msg},
            'AckMsg': {'type': AckMsg, 'handler': self.handle_ack_msg},
            'LedMsg': {'type': LedMsg, 'handler': self.handle_led_msg},
            'DfuMsg': {'type': DfuMsg, 'handler': self.handle_dfu_msg},
            'TxPowerMsg': {'type': TxPowerMsg, 'handler': self.handle_tx_power_msg},
        }

        self.start()

    #Thread
    def run(self):
        while True:
            self.incoming_data_handler()

    def incoming_data_handler(self):
        raw_data, addr = self.reciver_sock.recvfrom(1024)  # buffer size is 1024 bytes
        msg = Message.get(raw_data)

        #If the message is not associated with this module, the message is discarded
        if (msg == None) or (msg.identifier != IDENTIFIER):
            return

        for msgType, handler in self.handlers.items():
            if isinstance(msg, handler['type']):
                handler['handler'](msg)
                break
        else:
            print("no handlers for " + msg.opcode)

    def broadcast_data(self, encoded_data):
        self.broadcast_sock.sendto(encoded_data, (self.broadcast_ip, self.broadcast_port))

    def handle_iamalive(self, msg):
        self.sig_i_am_alive.emit(msg)

    def handle_start_sync_line(self, msg):
        self.sig_start_sync_line.emit(msg)

    def handle_stop_sync_line(self, msg):
        self.sig_stop_sync_line.emit(msg)

    def handle_start_time_sync(self, msg):
        self.sig_start_time_sync.emit(msg)

    def handle_stop_time_sync(self, msg):
        self.sig_stop_time_sync.emit(msg)

    def handle_reset_msg(self, msg):
        self.sig_reset_msg.emit(msg)

    def handle_ack_msg(self, msg):
        self.sig_ack_msg.emit(msg)

    def handle_led_msg(self, msg):
        self.sig_led_msg.emit(msg)

    def handle_dfu_msg(self, msg):
        self.sig_dfu_msg.emit(msg)

    def handle_tx_power_msg(self, msg):
        self.sig_tx_power_msg.emit(msg)




