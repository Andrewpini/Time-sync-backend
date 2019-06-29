# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys
import math
"""
Created on Thu Jan 18 14:38:46 2018
@author: OzyOzk
"""

"""
If you are on a windows machine, after succesfully running the code once, if you
terminated and run again, you will get the following error
SerialException: could not open port 'COM3': PermissionError(13, 'Access is denied.', None, 5)
You need to either reset your Kernel or delete all environment variables. On Spyder,
this can be done in the Ipython console. Reset is inside the options menu on the top 
right of the console (Cog symbol). Remove all variables is to the left of the Cog by
the stop button.
Once I find a proper solution I will update the code. 
"""
val1 = 0
val2 = 0
val3 = 0
is_graph_added = False
LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'w']

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

    # def ret_and_inc_var(self):
    #     self.plot_var += self.increment
    #     return self.plot_var
    #
    # def update_buffer(self):
    #     i = self.buffer[buffersize]
    #     self.buffer[i] = self.buffer[i+size] = self.ret_and_inc_var()
    #     self.buffer[buffersize] = i = (i+1) % size
    #     return i


def poll_button(lineedit):
    return(lineedit.text())


def make_curves(x, px):
    global element_count, curves, curve_xdata, buffersize
    for x in range(element_count):
        curves[x] = px.plot()
        curve_xdata[x] = np.zeros(buffersize+1, int)


def shift_elements(buffer, csv):
    global size, buffersize, element_count
    i = buffer[buffersize]
    buffer[i] = buffer[i+size] = csv[0]
    buffer[buffersize] = i = (i+1) % size


def add_graph():
    global is_graph_added, curve_x
    is_graph_added = True
    curve_x = p1.plot(pen='r', name="Data 3")


def close_app():
    sys.exit()

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
b1.clicked.connect(add_graph)

b2 = QtGui.QPushButton("Close")
b2.clicked.connect(close_app)

# t1 = QtGui.QLineEdit("Enter Device Serial")

p1 = pg.PlotWidget()
p1.setRange(yRange=[0, 1000000])
p1.addLegend()
p1.showGrid(x=True, y=True, alpha=0.8)
p1.setLabel('left', 'Amplitude (16bit Signed)')

curve1 = p1.plot(pen='y', name="Data 1")
curve2 = p1.plot(pen='g', name="Data 2")

for i in range(3):
    new_curve = CurveObj(0, i)
    print(new_curve.increment)
    new_curve.curve = p1.plot(pen=LINECOLORS[i], name=LINECOLORS[i])
    new_curve.buffer = np.zeros(buffersize+1, int)
    curves.append(new_curve)
# curves.append(CurveObj(0,3))
# curves.append(CurveObj(0,2))
# curves[0].curve = p1.plot(pen='b', name="Data 1")
# curves[1].curve = p1.plot(pen='g', name="Data 2")
# curves[2].curve = p1.plot(pen='y', name="Data 3")


layout.addWidget(p1, 0, 0, 1, 3)
layout.addWidget(b1, 1, 0)
# layout.addWidget(t1, 1, 1)
layout.addWidget(b2, 1, 2)


buffer1 = np.zeros(buffersize+1, int)
buffer2 = np.zeros(buffersize+1, int)
buffer3 = np.zeros(buffersize+1, int)

x = 0


def update():
    global curve1, curve2, x, size, buffersize, val1, val2, val3, curve_x

    x += 1

    # i = buffer1[buffersize]
    # buffer1[i] = buffer1[i+size] = val1
    # val1 = val1 + 1
    # buffer1[buffersize] = i = (i+1) % size
    #
    # j = buffer2[buffersize]
    # buffer2[j] = buffer2[j+size] = val2
    # val2 = val2 + 3
    # buffer2[buffersize] = j = (j+1) % size
    #
    # curve1.setData(buffer1[i:i+size])
    # curve1.setPos(x, 0)
    # curve2.setData(buffer2[j:j+size])
    # curve2.setPos(x, 0)

    # j = curves[0].buffer[buffersize]
    # curves[0].buffer[j] = curves[0].buffer[j+size] = curves[0].plot_var
    # curves[0].plot_var = curves[0].plot_var + 2
    # curves[0].buffer[buffersize] = j = (j+1) % size
    #
    # curves[0].curve.setData(curves[0].buffer[j:j+size])
    # curves[0].curve.setPos(x, 0)
    #
    # k = curves[1].buffer[buffersize]
    # curves[1].buffer[k] = curves[1].buffer[k+size] = curves[1].plot_var
    # curves[1].plot_var = curves[1].plot_var + curves[1].increment
    # curves[1].buffer[buffersize] = k = (k+1) % size
    #
    # curves[1].curve.setData(curves[1].buffer[k:k+size])
    # curves[1].curve.setPos(x, 0)

    for curve in curves:
        k = curve.buffer[buffersize]
        curve.buffer[k] = curve.buffer[k + size] = curve.plot_var
        curve.plot_var = curve.plot_var + curve.increment
        curve.buffer[buffersize] = k = (k + 1) % size

        curve.curve.setData(curve.buffer[k:k + size])
        curve.curve.setPos(x, 0)

    print(curves[1].buffer)
    print(curves[0].buffer)
    # if is_graph_added:
    #
    #     k = buffer3[buffersize]
    #     buffer3[k] = buffer3[k + size] = val3
    #     val3 = val3 + 2
    #     buffer3[buffersize] = k = (k + 1) % size
    #
    #     curve_x.setData(buffer3[k:k + size])
    #     curve_x.setPos(x, 0)
    #     print(k)
    #     print(buffer3)


    app.processEvents()


def write_hei():
    print(val1)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(dt)
timer.setInterval(dt)

# timer2 = QtCore.QTimer()
# timer2.timeout.connect(write_hei)
# timer2.start(200)
# timer2.setInterval(200)
# if(ser != None):
#  timer.stop()
win.show()
app.exec_()

