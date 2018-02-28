import sys
from calc import distance
import pymysql
import math

# Open database connection
#db = pymysql.connect(host = "positioning.cbgkbhphknqn.us-east-2.rds.amazonaws.com", user = "jtguggedal", passwd = "", db = "positioning_db", port = #3306, cursorclass = pymysql.cursors.DictCursor)
db = pymysql.connect(host = "localhost", user = "root", passwd = "admin", db = "positioning", port = 3306, cursorclass = pymysql.cursors.DictCursor)

# prepare a cursor object using cursor() method
cursor = db.cursor()
print("Connected to database")


def main(args):

	sql = "SELECT * FROM `positioning`.`rssi_data` WHERE CRC = 1 AND Address = '00:ce:11:52:a6:0f' ORDER BY `Date` DESC LIMIT 10"
	cursor.execute(sql)
	row = cursor.fetchone()

	while row:
		rssi =  row['RSSI']
		channel = row['Channel']
		f = distance.bleChannelToFrequency(channel)

		# Log distance
		rssi_d0 = -40.0
		d0 = 1.0
		n = 2.6
		xo = 14.1

		dist_1 = round(distance.logDistancePathLoss(rssi, rssi_d0, d0, n, xo), 2)

		# ITU distance model
		N = 30
		Lf = 14
		n = 1
		
		dist_2 = round(distance.ituDistance(rssi, f, N, Lf, n), 2)

		# Empirical model
		n = 4
		A = -45.0

		dist_3 = round(distance.empiricalDistance(rssi, n, A), 2)

		
		print("RSSI: ", rssi, "\t Channel: ", channel, "\t Log-dist: ", dist_1, "\t ITU: ", dist_2, "\t Empirical: ", dist_3)
		row = cursor.fetchone()
		



if __name__ == "__main__":
   main(sys.argv[1:])
