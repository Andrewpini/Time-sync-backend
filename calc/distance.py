import math

# Function to convert BLE advertising channel to frequency in MHz
def bleChannelToFrequency(channel):
	if channel == 37:
		f = 2402
	elif channel == 38:
		f = 2426
	elif channel == 39:
		f = 2480

	return f


# Log-Distance Path Loss model
# Basic form: RSSI = RSSI(d0) + 10nlog(d/d0) + Xo
# rssi is measured RSSI
# rssi_d0 is RSSI at distance d0
# n is the path loss exponent
# xo is zero-mean Gaussian distributed random variable with standard deviation to compensate for shadowing effects
def logDistancePathLoss(rssi, rssi_d0, d0, n, xo):
	rhs = (math.fabs(rssi) - math.fabs(rssi_d0) - xo) / (10 * n)
	distance = d0 * math.pow(10, rhs)

	return distance


# ITU's recommended model for indoor environments
# Basic form: Ltotal = L(d0) + N log(d/d0) + Lf(n) 	[dB], L(d0) = 20 log(f) - 28, f in MHz and d0 = 1m
# rssi is measured RSSI
# f is frequency in MHz at which RSSI was sampled
# N is the distance power loss, typically 28 for residential building, 30 for office
# Lf(n) is floor penetration loss factor, = 14 for typical office environment, 10 for typical apartment, 5 for a house
# n is the number of floors the signal propagates across
def ituDistance(rssi, f, N, Lf, n):
	Lfn = Lf * n 
	Ld0 = 20 * math.log(f, 10) - 28
	d0 = 1
	
	rhs = (math.fabs(rssi) - Ld0 - Lfn) / N
	distance = math.pow(10, rhs) * d0

	return distance


# Empirical RSSI-distance model
# Basic form: RSSI = 10nlog(d) + A
# rssi is measured RSSI
# n is path loss exponent
# A is measured RSSI at distance of 1m
def empiricalDistance(rssi, n, A):
	rhs = (math.fabs(rssi) - math.fabs(A)) / (10. * n)
	distance = math.pow(10, rhs)

	return distance
