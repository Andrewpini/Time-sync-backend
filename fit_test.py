import numpy as np
from filterpy.kalman import KalmanFilter
 
from calc import multilateration as multi
from calc import distance as dist

testData = [(0, 0, 2.344), 
			(3, 0, 2.912), 
			(6, 0, 6.223), 
			(0, 3, 1.323),
			(3, 3, 2.801),
			(6, 3, 5.712),
			(0, 6, 3.288),
			(3, 6, 7.149),
			(6, 6, 5.025) ]
	


def main():
	
	data = sorted(testData, key=lambda x: x[2])
	
	est = multi.multilateration(data[:], plotEnabled=True)


	print(est)
	

if __name__ == "__main__":
	main()

