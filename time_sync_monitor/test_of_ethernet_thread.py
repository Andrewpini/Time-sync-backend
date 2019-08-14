import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import ethernet_communication
import time

class DummyThread(QtCore.QThread):

    def __init__(self, parent=None):
        super(DummyThread, self).__init__(parent)
        self.start()

    #Thread
    def run(self):
        while True:
            print('Dummy')
            time.sleep(1)


def print_ting(addr, data):
        print(addr)
        print(data.decode())

ethernet = ethernet_communication.EthernetCommunicationThread("0.0.0.0", 11001, "255.255.255.255", 10000)
ethernet.incoming_ethernet_data_sig.connect(print_ting)

dummy = DummyThread()

app = QtWidgets.QApplication(sys.argv)
sys.exit(app.exec_())
