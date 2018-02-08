import socket
import json

import pymysql

# Open database connection
db = pymysql.connect("localhost","root","admin","positioning", cursorclass = pymysql.cursors.DictCursor)

# prepare a cursor object using cursor() method
cursor = db.cursor()

UDP_IP = "0.0.0.0"
UDP_PORT = 15000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
counter = 1
times = {"192.168.14.82" : 0, "192.168.14.86" : 0, "192.168.14.87" : 0}

while True:
	rawData, addr = sock.recvfrom(1024)
	data = json.loads(rawData)

	delta = data['timestamp'] - times[addr[0]]
	times[addr[0]] = data['timestamp']
	print(counter , "\tFrom", addr[0], "\tTimestamp: ", times[addr[0]], "\tAddr.: ", data['address'], "\tChannel: ", data['channel'], "\tRSSI: ", data['RSSI'], "\tCRC: ", data['CRC'], "\tLPE: ", data['LPE']) 
	counter += 1
	sql = "INSERT INTO rssi_data VALUES(null, '%s', '%d', '%s', %d, %d, %d, %d)" % (addr[0], data['timestamp'] , data['address'], data['channel'], data['RSSI'], data['CRC'], data['LPE'])

	number_of_rows = cursor.execute(sql)
	db.commit()
