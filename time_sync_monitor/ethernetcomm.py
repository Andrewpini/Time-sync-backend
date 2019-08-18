from PyQt5 import QtCore, QtGui, QtWidgets
import socket
from ethernetmsg import *

class EthernetCommunicationThread(QtCore.QThread):

    incoming_ethernet_data_sig = QtCore.pyqtSignal(object)

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
            'StartSyncLineAck': {'type': StartSyncLineAckMsg, 'handler': self.handle_start_sync_line_ack},
            'StopSyncLineAck': {'type': StopSyncLineAckMsg, 'handler': self.handle_stop_sync_line_ack},
            'StartTimeSyncAck': {'type': StartTimeSyncAckMsg, 'handler': self.handle_start_time_sync_ack},
            'StopTimeSyncAck': {'type': StopTimeSyncAckMsg, 'handler': self.handle_stop_time_sync_ack},
        }

        self.start()

    #Thread
    def run(self):
        while True:
            self.incoming_data_handler()

    def handle_iamalive(self, msg):
        self.incoming_ethernet_data_sig.emit(msg)

    def handle_start_sync_line(self, msg):
        print('STARTER TIMESYNC LINJE')

    def handle_stop_sync_line(self, msg):
        print('STOPPER TIMESYNC LINJE')

    def handle_start_time_sync(self, msg):
        print('STARTER TIMESYNC')

    def handle_stop_time_sync(self, msg):
        print('STOPPER TIMESYNC')

    def handle_start_sync_line_ack(self, msg):
        print('ACK1')

    def handle_stop_sync_line_ack(self, msg):
        print('ACK2')

    def handle_start_time_sync_ack(self, msg):
        print('ACK3')

    def handle_stop_time_sync_ack(self, msg):
        print('ACK4')

    def incoming_data_handler(self):
        raw_data, addr = self.reciver_sock.recvfrom(1024)  # buffer size is 1024 bytes
        msg = Message.get(raw_data)
        for msgType, handler in self.handlers.items():
            if isinstance(msg, handler['type']):
                handler['handler'](msg)
                break
        else:
            print("no handlers for " + msg.opcode)



    def broadcast_data(self, encoded_data):
        self.broadcast_sock.sendto(encoded_data, (self.broadcast_ip, self.broadcast_port))


