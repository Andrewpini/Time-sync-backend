#!/usr/bin/python3

import pymysql

# Open database connection
db = pymysql.connect("localhost","root","admin","positioning", cursorclass = pymysql.cursors.DictCursor)

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("SELECT * FROM rssi_data")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()
print (data['IP'])

# disconnect from server
db.close()