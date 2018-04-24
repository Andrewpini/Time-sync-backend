import matplotlib.pyplot as plt
 
import numpy as np
from scipy.optimize import leastsq

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

def multilateration(data, startingPoint=p0, plotEnabled=False, dimensions=3):
    def residuals(point, data):
        if dimensions == 2:
            p0[2] = 0
            return np.array([np.sqrt( np.square(p[0] - point[0]) + np.square(p[1] - point[1])) / abs(p[3]) - 1 for p in data])
        elif dimensions == 3:
            return np.array([np.sqrt( np.square(p[0] - point[0]) + np.square(p[1] - point[1]) + np.square(p[2] - point[2])) / abs(p[3]) - 1 for p in data])

    plsq = leastsq(residuals, p0, args=(data))
    
    if plotEnabled:
        fig = plt.figure()
        plt.ion()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlim((-5, 13))
        ax.set_ylim((-5, 13))
        x0,x1 = ax.get_xlim()
        y0,y1 = ax.get_ylim()
        ax.set_aspect(abs(x1-x0)/abs(y1-y0))

        # Plot section
        for p in data:
            circ = plt.Circle((p[0], p[1]), radius=p[3], color='b', alpha=0.1)
            circ2 = plt.Circle((p[0], p[1]), radius=0.01, color='r', alpha=1)
            ax.add_patch(circ)
            ax.add_patch(circ2)
        
        circ = plt.Circle(plsq[0], radius=0.15, color='r', alpha=1)
        ax.add_patch(circ)
        plt.show()

    
    return (round(plsq[0][0], 2), round(plsq[0][1], 2), round(plsq[0][2], 2))
