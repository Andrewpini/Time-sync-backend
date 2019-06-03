
import time


teller1 = 0
teller2 = 0
while True:
    teller2 += 1
    teller1 += 1
    log_file = open("w2f.txt", "a")
    log_file.write(str(teller1) + "," + str(teller2) + "\n")
    log_file.close()
    print(str(teller1) + "," + str(teller2) + "\n")

    time.sleep(1)
