from PyQt5 import QtCore, QtGui, QtWidgets
import socket


class EthernetCommunicationThread(QtCore.QThread):

    incoming_ethernet_data_sig = QtCore.pyqtSignal(str, str, str)

    def __init__(self, listen_ip, listen_port, broadcast_ip, broadcast_port, parent=None):
        super(EthernetCommunicationThread, self).__init__(parent)
        self.reciver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reciver_sock.bind((listen_ip, listen_port))

        self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.broadcast_ip = broadcast_ip
        self.broadcast_port = broadcast_port

        self.start()

    #Thread
    def run(self):
        while True:
            self.incoming_data_handler()

    def incoming_data_handler(self):
        raw_data, addr = self.reciver_sock.recvfrom(1024)  # buffer size is 1024 bytes
        self.incoming_ethernet_data_sig.emit(str(addr[0]), str(raw_data), 'Ting')

    def broadcast_data(self, encoded_data):
        self.broadcast_sock.sendto(encoded_data, (self.broadcast_ip, self.broadcast_port))

