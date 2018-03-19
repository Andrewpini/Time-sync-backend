import matplotlib.pyplot as plt
 
from numpy import *
from scipy.optimize import leastsq
 
allPoints = [ 	(0, 8, 4.76), 
			(0, 0, 4.299), 
			(8, 4, 4.902), 
			(2.47, 15.639, 11.047),
			(15, 10, 12.744) ]
 
def residuals(point, data):
    return array([sqrt( square(p[0] - point[0]) + square(p[1] - point[1])) / abs(p[2]) - 1 for p in data])
 
p0 = [0, 0]
 
points = allPoints[:5]
plsq = leastsq(residuals, p0, args=(points))
print(plsq)
 
 
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_xlim((-15, 20))
ax.set_ylim((-5, 30))
x0,x1 = ax.get_xlim()
y0,y1 = ax.get_ylim()
ax.set_aspect(abs(x1-x0)/abs(y1-y0))


# Plot section
for p in points:
        circ = plt.Circle((p[0], p[1]), radius=p[2], color='b', alpha=0.5)
        circ2 = plt.Circle((p[0], p[1]), radius=0.01, color='r', alpha=1)
        ax.add_patch(circ)
        ax.add_patch(circ2)
 
circ = plt.Circle(plsq[0], radius=0.15, color='r', alpha=1)
ax.add_patch(circ)
plt.show()