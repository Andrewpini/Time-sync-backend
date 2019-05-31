'''
my_list = []
my_list.append(['10.0.0.11',2,5])
my_list.append([123,'tiss'])

#print(my_list)


dick = {}
dick["10.0.0.11"] = {"Farge": 'grønn', "x_coordinate": [], "y_coordinate": []}

ting = dick["10.0.0.11"]["Farge"]
print(ting)'''

import numpy as np
from matplotlib import pyplot as plt


def main():
    plt.axis([-50,50,0,10000])
    plt.ion()

    x = np.arange(-50, 51)
    for pow in range(1,5):   # plot x^1, x^2, ..., x^4
        y = [Xi**pow for Xi in x]
        plt.plot(x, y)
        plt.draw()
        plt.pause(0.001)
        input("Press [enter] to continue.")

if __name__ == '__main__':
    main()