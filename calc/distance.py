import math
import statistics
import numpy as np

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
# Basic form: RSSI = RSSI(d0) - 10nlog(d/d0) + Xo
# rssi is measured RSSI
# rssi_d0 is RSSI at distance d0
# n is the path loss exponent
# Xo is zero-mean Gaussian distributed random variable with standard deviation to compensate for shadowing effects
def logDistancePathLoss(rssi, rssi_d0, d0, n, stDev=6.0):
    Xo = np.random.normal(loc=0.0, scale=stDev)
    rhs = -(rssi - rssi_d0 - Xo) / (10 * n)
    distance = d0 * math.pow(10, rhs)

    return distance

# Function to calculate the path loss exponent used by Log-Distance Path loss model
def calcPathLossExponent(rssi, d, rssi_d0, d0, xo):
    n = (rssi_d0 - rssi) / (10 * math.log10(d/d0))

    return n

def altMethod(rssi, X, n):
    return math.pow((rssi/X), ((-1)/n))
    

# ITU's recommended model for indoor environments
# Basic form: Ltotal = L(d0) + N log(d/d0) + Lf(n) 	[dB], L(d0) = 20 log(f) - 28, f in MHz and d0 = 1m
# rssi is measured RSSI
# f is frequency in MHz at which RSSI was sampled
# N is the distance power loss, typically 28 for residential building, 30 for office
# Lf(n) is floor penetration loss factor, = 14 for typical office environment, 10 for typical apartment, 5 for a house
# n is the number of floors the signal propagates across
def ituDistance(rssi, f, N=30, Lf=14, n=1):
    Lfn = Lf * n 
    Ld0 = 20 * math.log10(f) - 28
    d0 = 1
    
    rhs = (math.fabs(rssi) - Ld0 - Lfn) / N
    distance =  d0 * math.pow(10, rhs)

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
