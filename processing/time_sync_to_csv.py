import csv
import datetime

now = datetime.datetime.now()
file_name = "raw_sync_data_" + now.strftime("%d-%m-%Y(%H_%M)") + ".csv"

thisdict ={
  "Event_ID": 1,
  "Node": 100,
  "Timestamp(in microsec)": 123456
}

with open(file_name, 'w', newline='') as csvfile:
    fieldnames = ['Event_ID', 'Node', 'Timestamp(in microsec)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow(thisdict)
