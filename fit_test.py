import numpy as np
from filterpy.kalman import KalmanFilter
 
from calc import multilateration as multi
from calc import distance as distance

testData = [(0, 0, 0, 2.344), 
			(3, 0, 0, 2.912), 
			(6, 0, 0, 6.223), 
			(0, 3, 0, 1.323),
			(3, 3, 0, 2.801),
			(6, 3, 0, 5.712),
			(0, 6, 0, 3.288),
			(3, 6, 0, 7.149),
			(6, 6, 0, 5.025) ]


altData = [	(475060, 1096300, 4670, 5940.893),
			(481500, 1094900, 4694, 2420.883),
			(482230, 1088430, 4831, 5087.666),
			(478050, 1087810, 4775, 5545.271),
			(471430, 1088580, 4752, 9643.044),
			(468720, 1091240, 4803, 11417.270),
			(467400, 1093980, 4705, 12638.110),
			(468730, 1097340, 4747, 12077.030)
]

altData2 = [(0, 0, 5, 2.999999),
			(0, -7.48, 0, 6.577993615),
			(5, 0, 0, 8.0118662)
]

altData3 = [(1.900000, 7.450000, 2.700000, 14.678),
						(1.300000, 6.250000, 2.700000, 2.4484),
						(3.810000, 2.070000, 2.700000, 10),
						(3.810000, 3.250000, 2.700000, 5.275),
						(1.300000, 2.070000, 2.700000, 8.7992),
						(0.100000, 6.850000, 2.700000, 2.7826),
						(1.300000, 3.850000, 2.700000, 8.7992),	
						(3.700000, 5.050000, 2.700000, 166.8101)]

altData4 = [(3.81, 3.25, 2.7, 0.9215),
						(3.7, 5.05, 2.7, 1.0850),
						(1.3, 3.85, 2.7, 2.4551),
						(0.1, 6.85, 2.7, 1.0850),
						(3.81, 2.07, 2.7, 2.890),
						(1.3, 2.07, 2.7, 2.0852),
						(1.9, 7.45, 2.7, 1.2775),	
						(1.3, 6.25, 2.7, 1.5041)]

def main():
	LOG_DISTANCE_ST_DEV = 0.0
	LOG_DISTANCE_N = 1.41
	LOG_DISTANCE_RSSI_D0 = 43.5
	LOG_DISTANCE_D0 = 1.0
	rssi = -46
	
	#d = distance.logDistancePathLoss(rssi, rssi_d0=-LOG_DISTANCE_RSSI_D0, d0=LOG_DISTANCE_D0, n=LOG_DISTANCE_N, stDev=LOG_DISTANCE_ST_DEV)
	#print(d)

	data = sorted(altData4, key=lambda x: x[3])
	
	est = multi.multilateration(data[:], dimensions=3, plotEnabled=True)


	print(est)

	input("Press close to exit") 
	

if __name__ == "__main__":
	main()

