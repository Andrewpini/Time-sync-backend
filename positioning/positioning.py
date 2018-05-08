import numpy as np
from filterpy.kalman import KalmanFilter
from calc import multilateration as multi

class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def enableKalman(self, x, F, H, P, R, Q, dim_x=4, dim_z=2):
        self.kalman = KalmanFilter(dim_x=dim_x, dim_z=dim_z)
        self.kalman.x = x
        self.kalman.F = F
        self.kalman.H = H
        self.kalman.P = P
        self.kalman.R = R
        self.kalman.Q = Q

    def updatePosition(self, pos):
        self.kalman.update(pos)
        self.x = self.kalman.x[0]
        self.y = self.kalman.x[2]
        self.z = self.kalman.x[4]

        return (self.x, self.y, self.z)

    def setKalmanX(self, x):
        self.kalman.x = np.array(x)


class Tag:
    def __init__(self, address="", currentCounter=0, currentCounterAdvCount=0):
        self.address = address
        self.currentCounter = currentCounter
        self.currentCounterAdvCount = currentCounterAdvCount
        self.rssi = list()
        self.filteredRssi = 0
        self.distance = 0
        self.kalman = KalmanFilter(dim_x=1, dim_z=1)
        self.kalman.x = np.array([[-49.]])
        self.kalman.F = np.array([[1.]])
        self.kalman.H = np.array([[1.]])
        self.kalman.P = np.array([[0.]])
        self.kalman.R = 3.19
        self.kalman.Q = 0.065
        self.kalman.batch_filter

    def setKalmanParameters(self, x, F, H, P, R, Q, dim_x=1, dim_z=1):
        self.kalman = KalmanFilter(dim_x=dim_x, dim_z=dim_z)
        self.kalman.x = x
        self.kalman.F = F
        self.kalman.H = H
        self.kalman.P = P
        self.kalman.R = R
        self.kalman.Q = Q
    
    def setKalmanX(self, x):
        self.kalman.x = np.array([[x]])

    def setKalmanQ(self, Q):
        self.kalman.Q = Q

    def setKalmanR(self, R):
        self.kalman.R = R



class Node:
    def __init__(self, nodeID, ip='', x=0, y=0, z=0, active=False):
        self.nodeID = nodeID
        self.position = Position(x, y, z)
        self.tags = dict()
        self.ip = ip
        self.active = active

    def setActiveStatus(self, value):
        self.active = value

    def getActiveStatus(self):
        return self.active

    def addTag(self, address):
        self.tags[address] = Tag()

    def setPosition(self, pos):
        self.position = Position(pos[0], pos[1], pos[2])



'''
class Positioning:
    def __init__(self):
        self.nodes = list()

    def multilateration(self):
        data = []
        return multi.multilateration()
'''