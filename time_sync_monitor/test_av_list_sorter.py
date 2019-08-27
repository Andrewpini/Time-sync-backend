import time
import random

nasse = []
brum = 6



while True:
    brum = random.randint(0,50)


    if not nasse:
        nasse.append(brum)
    else:
        for idx in range(len(nasse)):
            if brum < nasse[idx]:
                nasse.insert(idx, brum)
                break
            if idx == len(nasse) - 1:
                nasse.append(brum)
    print(nasse)
    time.sleep(1)