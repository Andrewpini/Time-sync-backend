
 
import numpy as np
from scipy.optimize import leastsq, least_squares, minimize

testData = [(0, 0, 2, 5.144), 
            (3, 0, 2, 4.612), 
            (6, 0, 2, 6.223), 
            (0, 3, 2, 2.323),
            (3, 3, 2, 2.301),
            (6, 3, 2, 5.712),
            (0, 6, 2, 1.288),
            (3, 6, 2, 1.949),
            (6, 6, 2, 5.025) ]
    
p0 = [1, 1, 1.5]

def multilateration(data, startingPoint=p0, plotEnabled=False, dimensions=3, bounds=([-2, 0, 0], [5, 11, 3])):
    def residuals(point, *data):
        if dimensions == 2:
            point[2] = 0
            #return np.array([np.square(np.sqrt( np.square(p[0] - point[0]) + np.square(p[1] - point[1])) - p[3]) / np.square(p[3]) for p in data])
            return np.array([np.sqrt( np.square(p[0] - point[0]) + np.square(p[1] - point[1])) / p[3] - 1 for p in data])
        elif dimensions == 3:
            return np.array([np.square(np.sqrt( np.square(p[0] - point[0]) + np.square(p[1] - point[1]) + np.square(p[2] - point[2])) - p[3]) / (p[3])**3 for p in data])
            #return np.array([np.sqrt( np.square(p[0] - point[0]) + np.square(p[1] - point[1]) + np.square(p[2] - point[2])) / p[3] - 1 for p in data])
    
    #plsq = leastsq(residuals, startingPoint, args=(data))
    plsq = least_squares(residuals, startingPoint, args=data, bounds=bounds)

    return (round(plsq['x'][0], 2), round(plsq['x'][1], 2), round(plsq['x'][2], 2))
    #return (round(plsq[0][0], 2), round(plsq[0][1], 2), round(plsq[0][2], 2))
