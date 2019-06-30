from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys
import random

LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'w']
NODES = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf']
active_nodes = {}
dummy_counter = 0

dt = 1000  # Time delta in milliseconds
element_count = 0
curves = list()
curve_xdata = list()
curve_x = object

size = 10
buffersize = 2*10


class CurveObj:

    def __init__(self, var, inc):
        self.plot_var = var
        self.increment = inc

    buffer = object
    curve = object


def close_app():
    sys.exit()


def add_curve():
    global dummy_counter, LINECOLORS, active_nodes, NODES
    new_curve = CurveObj(0, random.randint(1, 10))
    new_curve.curve = p1.plot(pen=LINECOLORS[dummy_counter], name=NODES[dummy_counter])
    new_curve.buffer = np.zeros(buffersize+1, int)
    curves.append(new_curve)
    dummy_counter += 1

# for Spyder. When you close your window, the QtApplicaiton instance is
# still there after being created once. Therefore check if a Qt instance
# already exists, if it does, then use it, otherwise, create new instance
if not QtGui.QApplication.instance():
    app = QtGui.QApplication([])
else:
    app = QtGui.QApplication.instance()

win = QtGui.QWidget()
win.setWindowTitle("Time sync plot")
win.resize(1000, 600)
layout = QtGui.QGridLayout()
win.setLayout(layout)

b1 = QtGui.QPushButton("Add graph")
b1.clicked.connect(add_curve)

b2 = QtGui.QPushButton("Close")
b2.clicked.connect(close_app)

p1 = pg.PlotWidget()
p1.setRange(yRange=[0, 1000000])
p1.addLegend()
p1.showGrid(x=True, y=True, alpha=0.8)
p1.setLabel('left', 'Amplitude (16bit Signed)')

# zxc = p1.plot([1,2,3],[1,2,3],pen='y', name='Tiss')


layout.addWidget(p1, 0, 0, 1, 3)
layout.addWidget(b1, 1, 0)
layout.addWidget(b2, 1, 2)

x = 0


def update():
    global x, size, buffersize
    # x += 1
    for curve in curves:
        k = curve.buffer[buffersize]
        curve.buffer[k] = curve.buffer[k + size] = curve.plot_var
        curve.plot_var = curve.plot_var + random.randint(-5,5)
        curve.buffer[buffersize] = k = (k + 1) % size
        curve.curve.setData(curve.buffer[k:k + size])
        # zxc.setData([1,2,3,5,6], [1,2,3,2, 1])
        # curve.curve.setPos(x, 0)
        print(curve.buffer)
    app.processEvents()


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(dt)
timer.setInterval(dt)

win.show()
app.exec_()

