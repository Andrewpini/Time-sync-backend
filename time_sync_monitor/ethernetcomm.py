from PyQt5 import QtCore, QtGui, QtWidgets
import socket


class EthernetCommunicationThread(QtCore.QThread):

    incoming_ethernet_data_sig = QtCore.pyqtSignal(bytes)

    def __init__(self, listen_ip, listen_port, broadcast_ip, broadcast_port, parent=None):
        super(EthernetCommunicationThread, self).__init__(parent)
        self.reciver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reciver_sock.bind((listen_ip, listen_port))

        self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.broadcast_ip = broadcast_ip
        self.broadcast_port = broadcast_port

        self.handlers = {
            'IAmAlive': EthernetCommunicationThread.handle_iamalive,
        }

        self.start()

    #Thread
    def run(self):
        while True:
            self.incoming_data_handler()

    def handle_iamalive(self, msg):
        pass

    def incoming_data_handler(self):
        raw_data, addr = self.reciver_sock.recvfrom(1024)  # buffer size is 1024 bytes
        # self.incoming_ethernet_data_sig.emit(b'\xce\xfa\xad\xde\xef\xb0\x95U;\x94\xa4\n\x00\x00\x0b')
        msg = Message.get(raw_data)
        for msgType, handler in self.handlers.items():
            if isinstance(msg, msgType):
                handler(self, msg)
                break
        else:
            print("no handlers for " + msg.opcode)



    def broadcast_data(self, encoded_data):
        self.broadcast_sock.sendto(encoded_data, (self.broadcast_ip, self.broadcast_port))

