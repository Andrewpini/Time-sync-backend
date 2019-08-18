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
        }

        self.start()

    #Thread
    def run(self):
        while True:
            self.incoming_data_handler()

    def handle_iamalive(self, msg):
        self.incoming_ethernet_data_sig.emit(msg)


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


