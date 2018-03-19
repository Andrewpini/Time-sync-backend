import numpy as np
import math
from statistics import median

# Trilateration calculation function assuming perfect intersection in a single point
# Not for real-life use
def trilateration(x0, y0, r0, x1, y1, r1, x2, y2, r2):

	abIntersect = checkCircleIntersection(x0, y0, r0, x1, y1, r1)
	acIntersect = checkCircleIntersection(x0, y0, r0, x1, y1, r1)
	bcIntersect = checkCircleIntersection(x0, y0, r0, x1, y1, r1)

	allIntersect = abIntersect and acIntersect and bcIntersect

	if allIntersect:
		A = 2 * (x1 - x0)
		B = 2 * (y1 - y0)
		D = 2 * (x2 - x1)
		E = 2 * (y2 - y1)

		C = r0**2 - r1**2 - x0**2 + x1**2 - y0**2 + y1**2
		F = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2

		x = (C*E - B*F) / (A*E - B*D)
		y = (C*D - A*F) / (B*D - A*E)

	return {'x': x, 'y': y}

# Function to check if two circels intersect
def checkCircleIntersection(x0, y0, r0, x1, y1, r1):
	return math.hypot(x0-x1, y0-y1) <= (r0 + r1)


def channelSelect(channelData, mode='max'):
	if mode == 'max':
		return max(channelData)
	elif mode == 'avg':
		return np.mean(channelData)
	elif mode == 'median':
		return median(channelData)
