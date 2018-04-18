import numpy as np
from filterpy.kalman import KalmanFilter
 
from calc import multilateration as multi
from calc import distance as dist

testData = [(0, 0, 0, 2.344), 
			(3, 0, 0, 2.912), 
			(6, 0, 0, 6.223), 
			(0, 3, 0, 1.323),
			(3, 3, 0, 2.801),
			(6, 3, 0, 5.712),
			(0, 6, 0, 3.288),
			(3, 6, 0, 7.149),
			(6, 6, 0, 5.025) ]


altData = [	(475060, 1096300, 4670, 5940),
			(481500, 1094900, 4694, 2420),
			(482230, 1088430, 4831, 5087),
			(478050, 1087810, 4775, 5545),
			(471430, 1088580, 4752, 9643),
			(468720, 1091240, 4803, 11417),
			(467400, 1093980, 4705, 12638),
			(468730, 1097340, 4747, 12077)
]

altData2 = [(0, 0, 5, 2.999999),
			(0, -7.48, 0, 6.577993615),
			(5, 0, 0, 8.0118662)
]


def main():
	
	data = sorted(testData, key=lambda x: x[3])
	
	est = multi.multilateration(data[:], plotEnabled=True)


	print(est)

	k = input("Press close to exit") 
	

if __name__ == "__main__":
	main()

