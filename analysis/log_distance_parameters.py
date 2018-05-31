import pymysql
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

tableName = "position_testing"
label = "Positioning test - elevated nodes,"
labelLength = len(label)
address = 'd5:ce:11:52:a6:0f' #%14:60:d6:26:46:b6'; %"47:c5:1c:ff:47:c5";
selection = 'NodeID, Channel, Counter, Address, RSSI, Node_position, True_tag_position'
limit = 100000000
alpha = 0.01
axes = [0, 10, -100, -20]
dotColor = 'k'
lineColor = 'r'
labelDots = None
dotSize = 12


def euclideanDistance(a, b):
  ret = list()
  for i in range(0, len(a)):
    ret.append(np.sqrt(np.square(a[i][0] - b[i][0]) + np.square(a[i][1] - b[i][1]) + np.square(a[i][2] - b[i][2])))
  return ret


# Set up DB connection
conn = pymysql.connect(host = 'localhost', user = 'root', passwd = 'admin', db = 'positioning', port = 3306, cursorclass = pymysql.cursors.DictCursor)

# prepare a cursor object using cursor() method
cursor = conn.cursor()
print("Connected to database")

q_37    = "SELECT %s FROM %s WHERE CRC LIKE 1 AND LPE LIKE 0 AND Channel LIKE 37 AND LEFT(Label, %d) LIKE LEFT('%s', %d) AND LEFT(True_tag_position, 1) LIKE '('  AND Address LIKE '%s' LIMIT %d" % (selection, tableName, labelLength, label, labelLength, address, limit)
q_38    = "SELECT %s FROM %s WHERE CRC LIKE 1 AND LPE LIKE 0 AND Channel LIKE 38 AND LEFT(Label, %d) LIKE LEFT('%s', %d) AND LEFT(True_tag_position, 1) LIKE '('  AND LEFT(True_tag_position, 1)  AND Address LIKE '%s' LIMIT %d" % (selection, tableName, labelLength, label, labelLength, address, limit)
q_39    = "SELECT %s FROM %s WHERE CRC LIKE 1 AND LPE LIKE 0 AND Channel LIKE 39 AND LEFT(Label, %d) LIKE LEFT('%s', %d) AND LEFT(True_tag_position, 1) LIKE '(' AND Address LIKE '%s' LIMIT %d" % (selection, tableName, labelLength, label, labelLength, address, limit)
q_all   = "SELECT %s FROM %s WHERE CRC LIKE 1 AND LPE LIKE 0 AND LEFT(Label, %d) LIKE LEFT('%s', %d) AND LEFT(True_tag_position, 1) LIKE '('  AND Address LIKE '%s' LIMIT %d" % (selection, tableName, labelLength, label, labelLength, address, limit)

print("Reading from database")
#data_37 = pd.read_sql(q_37, conn)
#data_38 = pd.read_sql(q_38, conn)
#data_39 = pd.read_sql(q_39, conn)
data_all = pd.read_sql(q_all, conn)
data_37 = data_all.loc[data_all['Channel'] == 37]
data_38 = data_all.loc[data_all['Channel'] == 38]
data_39 = data_all.loc[data_all['Channel'] == 39]



print("Stats for 37: ", data_37.describe())
print("Stats for 38: ", data_38.describe())
print("Stats for 39: ", data_39.describe())
print("Stats for all: ", data_all.describe())

print("Getting node positions")
nodePositions_37 = [eval(x) for x in data_37['Node_position']]
nodePositions_38 = [eval(x) for x in data_38['Node_position']]
nodePositions_39 = [eval(x) for x in data_39['Node_position']]
nodePositions_all = [eval(x) for x in data_all['Node_position']]

print("Getting tag positions")
trueTagPositions_37 = [eval(x) for x in data_37['True_tag_position']]
trueTagPositions_38 = [eval(x) for x in data_38['True_tag_position']]
trueTagPositions_39 = [eval(x) for x in data_39['True_tag_position']]
trueTagPositions_all = [eval(x) for x in data_all['True_tag_position']]

print("Getting RSSIs")
rssis_37 = data_37['RSSI']
rssis_38 = data_38['RSSI']
rssis_39 = data_39['RSSI']
rssis_all = data_all['RSSI']

print("Starting distance calculations")
distances_37 = euclideanDistance(nodePositions_37, trueTagPositions_37)
print("Channel 37 done")
distances_38 = euclideanDistance(nodePositions_38, trueTagPositions_38)
print("Channel 38 done")
distances_39 = euclideanDistance(nodePositions_39, trueTagPositions_39)
print("Channel 39 done")
distances_all = euclideanDistance(nodePositions_all, trueTagPositions_all)
print("All channels done")



def fit(distances, rssis):
  def residuals(data, p1, p2):
    return np.array([p1 - 10.0 * p2 * np.log10(p) for p in data])

  startingPoint = [-40.0, 2.0]
  #plsq = leastsq(residuals, startingPoint, args=(distances_37))
  popt, _ = curve_fit(residuals, distances, rssis, p0=startingPoint)
  return popt

results_37 = fit(distances_37, rssis_37)
results_38 = fit(distances_38, rssis_38)
results_39 = fit(distances_39, rssis_39)
results_all = fit(distances_all, rssis_all)

print("For 37: \t A =", results_37[0], "\t n = ", results_37[1])
print("For 38: \t A =", results_38[0], "\t n = ", results_38[1])
print("For 39: \t A =", results_39[0], "\t n = ", results_39[1])
print("For all: \t A =", results_all[0], "\t n = ", results_all[1])

x = np.arange(0.001, 11, 0.01)
#y = [results_37[0] - 10.0 * results_37[1] * np.log10(x) for x in x]

label_37 = "A = %.1f, n = %.1f" % (results_37[0], results_37[1])
label_38 = "A = %.1f, n = %.1f" % (results_38[0], results_38[1])
label_39 = "A = %.1f, n = %.1f" % (results_39[0], results_39[1])
label_all = "A = %.1f, n = %.1f" % (results_all[0], results_all[1])

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rcParams['agg.path.chunksize'] = 10000
f, axarr = plt.subplots(2, 2)
axarr[0, 0].grid(b=True, which='major', color='k', alpha=0.3, linestyle='-')
axarr[0, 0].grid(b=True, which='minor', color='k', alpha=0.1, linestyle='--')
axarr[0, 0].minorticks_on()
axarr[0, 0].scatter(distances_37, rssis_37, color=dotColor, alpha=alpha, label=labelDots, s=dotSize)
axarr[0, 0].plot(x, [results_37[0] - 10.0 * results_37[1] * np.log10(x) for x in x], color=lineColor, label=label_37)
axarr[0, 0].set_title('Channel 37')
axarr[0, 0].legend()
axarr[0, 0].axis(axes)
axarr[0, 0].set_xlabel("Distance [m]")
axarr[0, 0].set_ylabel("RSSI [dBm]")
axarr[0, 1].grid(b=True, which='major', color='k', alpha=0.3, linestyle='-')
axarr[0, 1].grid(b=True, which='minor', color='k', alpha=0.1, linestyle='--')
axarr[0, 1].minorticks_on()
axarr[0, 1].scatter(distances_38, rssis_38, color=dotColor, alpha=alpha, label=labelDots, s=dotSize)
axarr[0, 1].set_title('Channel 38')
axarr[0, 1].plot(x, [results_38[0] - 10.0 * results_38[1] * np.log10(x) for x in x], color=lineColor, label=label_38)
axarr[0, 1].legend()
axarr[0, 1].axis(axes)
axarr[0, 1].set_xlabel("Distance [m]")
axarr[0, 1].set_ylabel("RSSI [dBm]")
axarr[1, 0].grid(b=True, which='major', color='k', alpha=0.3, linestyle='-')
axarr[1, 0].grid(b=True, which='minor', color='k', alpha=0.1, linestyle='--')
axarr[1, 0].minorticks_on()
axarr[1, 0].scatter(distances_39, rssis_39, color=dotColor, alpha=alpha, label=labelDots, s=dotSize)
axarr[1, 0].set_title('Channel 39')
axarr[1, 0].plot(x, [results_39[0] - 10.0 * results_39[1] * np.log10(x) for x in x], color=lineColor, label=label_39)
axarr[1, 0].legend()
axarr[1, 0].axis(axes)
axarr[1, 0].set_xlabel("Distance [m]")
axarr[1, 0].set_ylabel("RSSI [dBm]")
axarr[1, 1].grid(b=True, which='major', color='k', alpha=0.3, linestyle='-')
axarr[1, 1].grid(b=True, which='minor', color='k', alpha=0.1, linestyle='--')
axarr[1, 1].minorticks_on()
axarr[1, 1].scatter(distances_all, rssis_all, color=dotColor, alpha=alpha, label=labelDots, s=dotSize)
axarr[1, 1].set_title('All channels')
axarr[1, 1].plot(x, [results_all[0] - 10.0 * results_all[1] * np.log10(x) for x in x], color=lineColor, label=label_all)
axarr[1, 1].legend()
axarr[1, 1].axis(axes)
axarr[1, 1].set_xlabel("Distance [m]")
axarr[1, 1].set_ylabel("RSSI [dBm]")

plt.suptitle("\Large \\textbf{Log-distance path loss model parameter estimation}")
plt.show()

print("Finished")
