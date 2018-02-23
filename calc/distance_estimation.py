import math

def logDistancePathLoss(rssi, rssi_d0):
	
	a = 1
	return a

# Basic form: Ltotal = L(d0) + N log(d/d0) + Lf(n) 	[dB], L(d0) = 20 log(f) - 28, f in MHz and d0 = 1m
# f is frequency in MHz at which RSSI was sampled
# N is the distance power loss, typically 28 for residential building, 30 for office
# Lf(n) is floor penetration loss factor, = 14 for typical office environment, 10 for typical apartment, 5 for a house
# n is the number of floors
def ituDistance(rssi, f, N, Lf, n):
	Lf = Lf * n 
	Ld0 = 20 * math.log(f) - 28

	Ltotal = Ld0 + N * math.log(d/1) + Lf

	return Ltotal
