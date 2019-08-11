import sys
from PyQt5 import QtWidgets, QtGui

class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.le1 = QtWidgets.QLineEdit()
        self.le2 = QtWidgets.QLineEdit()

        self.b1 = QtWidgets.QPushButton('Start sync line')
        self.b2 = QtWidgets.QPushButton('Stop sync line')
        self.b3 = QtWidgets.QPushButton('Start synchronization')
        self.b4 = QtWidgets.QPushButton('Stop synchronization')
        self.b5 = QtWidgets.QPushButton('Reset')

        self.list = QtWidgets.QListWidget()



        h_box1 = QtWidgets.QHBoxLayout()
        h_box1.addWidget(self.b1)
        h_box1.addWidget(self.b2)

        h_box2 = QtWidgets.QHBoxLayout()
        h_box2.addWidget(self.b3)
        h_box2.addWidget(self.b4)

        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(self.le1)
        v_box.addLayout(h_box1)
        v_box.addSpacing(30)
        v_box.addWidget(self.le2)
        v_box.addLayout(h_box2)
        v_box.addWidget(self.b5)
        v_box.addWidget(self.list)

        self.setLayout(v_box)

        ting = 12
        self.list.addItem('penis')
        self.list.setEnabled()

        self.setWindowTitle('PyQt5 Lesson 6')

        self.show()

app = QtWidgets.QApplication(sys.argv)
a_window = Window()
sys.exit(app.exec_())