import matplotlib.pyplot as plt
 
import numpy as np
from scipy.optimize import leastsq

testData = [(0, 0, 5.144), 
			(3, 0, 4.612), 
			(6, 0, 6.223), 
			(0, 3, 2.323),
			(3, 3, 2.301),
			(6, 3, 5.712),
			(0, 6, 1.288),
			(3, 6, 1.949),
			(6, 6, 5.025) ]
	
p0 = [0, 0]

def multilateration(data, startingPoint=p0, plotEnabled=False):
	def residuals(point, data):
		return np.array([np.sqrt( np.square(p[0] - point[0]) + np.square(p[1] - point[1])) / abs(p[2]) - 1 for p in data])

	plsq = leastsq(residuals, p0, args=(data))
	
	if plotEnabled:
		fig = plt.figure()
		ax = fig.add_subplot(1, 1, 1)
		ax.set_xlim((-5, 13))
		ax.set_ylim((-5, 13))
		x0,x1 = ax.get_xlim()
		y0,y1 = ax.get_ylim()
		ax.set_aspect(abs(x1-x0)/abs(y1-y0))

		# Plot section
		for p in data:
			circ = plt.Circle((p[0], p[1]), radius=p[2], color='b', alpha=0.1)
			circ2 = plt.Circle((p[0], p[1]), radius=0.01, color='r', alpha=1)
			ax.add_patch(circ)
			ax.add_patch(circ2)
		
		circ = plt.Circle(plsq[0], radius=0.15, color='r', alpha=1)
		ax.add_patch(circ)
		plt.show()
	
	return plsq[0]
