import numpy as np
from filterpy.kalman import KalmanFilter

class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Tag:
    def __init__(self, address="", currentCounter=0, currentCounterAdvCount=0):
        self.address = address
        self.currentCounter = currentCounter
        self.currentCounterAdvCount = currentCounterAdvCount
        self.rssi = list()
        self.filteredRssi = 0
        self.distance = 0
        self.kalman = KalmanFilter(dim_x=1, dim_z=1)
        self.kalman.x = np.array([[-30.]])
        self.kalman.F = np.array([[1.]])
        self.kalman.H = np.array([[1.]])
        self.kalman.P = np.array([[0.]])
        self.kalman.R = 3.19
        self.kalman.Q = 0.065

    def setKalmanParameters(self, x, F, H, P, R, Q, dim_x=1, dim_z=1):
        self.kalman = KalmanFilter(dim_x=dim_x, dim_z=dim_z)
        self.kalman.x = x
        self.kalman.F = F
        self.kalman.H = H
        self.kalman.P = P
        self.kalman.R = R
        self.kalman.Q = Q

class Node:
    def __init__(self, nodeID, ip='', x=0, y=0, z=0):
        self.nodeID = nodeID
        self.position = Position(x, y, z)
        self.tags = dict()
        self.ip = ip