import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i) :
    graph_data = open('w2f.txt', 'r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    for line in lines :
        if len(line) > 1 :
            x, y = line.split(',')
            xs.append(x)
            ys.append(float(y))

    '''
    graph_data_b = open('eksempel_to.txt', 'r').read()
    lines_a = graph_data_b.split('\n')
    xa = []
    ya = []
    for line in lines_a :
        if len(line) > 1 :
            x, y = line.split(',')
            xa.append(x)
            ya.append(float(y))
    '''


    ax1.clear()
    ax1.plot(xs, ys)
    #ax1.plot(xa, ya)


ani = animation.FuncAnimation(fig, animate, interval=5000)
plt.show()



'''
#Grunnleggende graf
x = [1, 5, 3]
y = [51, 784, 345]

x2 = [1, 5, 3]
y2 = [21, 84, 35]

plt.plot(x, y, label='krake')
plt.plot(x2, y2, label='bake')
plt.show()
'''

'''
#import av fil med csv
x = []
y = []

with open('eksempel.txt','r') as csvfile:
    plot = csv.reader(csvfile, delimiter=',')
    for row in plot:
        x.append(int(row[0]))
        y.append(int(row[1]))

plt.plot(x, y)
'''

'''
#import av fil mednumpy
x, y = npy.loadtxt('eksempel.txt', delimiter=',', unpack=True)
plt.plot(x, y)
'''

'''
plt.xlabel('Ting')
plt.ylabel('Saker')
plt.title('Stor Flott Overskrift')
plt.legend()


plt.grid()

plt.show()
'''



