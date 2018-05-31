import pymysql
import numpy as np
import pandas as pd
import sys
import time
import os
from operator import itemgetter
sys.path.insert(0,'..')
from calc import distance
from calc import multilateration as multi
from positioning.positioning import Tag, Node, Position

# General settings
USE_WINDOWS           = False
SAVE_TO_CSV           = True    # Saves position estimates to CSV
SAVE_TO_PICKLE        = False
GET_DATA_FROM_FILE    = True
GET_DATA_FROM_DB      = False
PLOT_ENABLED          = False
ONLY_FILTERED         = True
USE_RSSI_FILTER       = False
SELECTIVE_PL_PARAMS   = False
USE_ALT_METHOD        = False

# CSV file settings
csvFolderPrefix       = "Test_888"

# Pickle dump settings
pickleDumpFolder      = "allPositions"

# DB query config
tableName             = "position_testing"
label                 = ''
address               =  None     #'d5:ce:11:52:a6:0f' #%14:60:d6:26:46:b6'; %"47:c5:1c:ff:47:c5";
selection             = 'NodeID, Channel, Counter, Address, RSSI, Node_position, True_tag_position'
limit                 = 100000000


# Plot configuration
title                 = "\\Large \\textbf{Position estimation with Kalman filtering on RSSI}"
radiusColor           = 'k'
nodePositionColor     = 'r'
truePositionColor     = 'g'
tagColor              = 'b'
rawTagColor           = 'k'
kalmanTagColor        = 'orange'
nodePositionDotRadius = 0.1
tagPositionDotRadius  = 0.15
dotColor              = 'k'
lineColor             = 'b'
dotSize               = 12
xaxis                 = (-3, 7)
yaxis                 = (-2, 11)

# Positioning configuration
numberOfIterations    = 80
numberOfNodesToUse    = 8
maxNumberOfNodes      = 8
multiStartingPoint    = [0, 0, 0.85]
multiBounds           = ([-2, 0, 0.84], [6, 11, 1.8])
log_d_n               = 1.78
d0                    = 1.0
rssi_d0               = -38.0
log_d_st_dev          = 0.8

altMethodX            = -38.4
altMethodN            = -0.17

altMethodParams = {
  37 : { "X" : -40.0, "n" : -0.14},
  38 : { "X" : -38.4, "n" : -0.16},
  39 : { "X" : -36.4, "n" : -0.20}
}


#logDistanceParams = {
#  37 : { "A" : -40.0, "n" : 1.59},
##  38 : { "A" : -38.0, "n" : 1.74},
 # 39 : { "A" : -36.1, "n" : 2.01}
#}

logDistanceParams = {
  37 : { "A" : -38.0, "n" : 1.84},
  38 : { "A" : -38.0, "n" : 1.74},
  39 : { "A" : -38.0, "n" : 1.76}
}

# Kalman filter for RSSI configuration
rssi_kalman_x         = -50.0
rssi_kalman_Q         = 0.07
rssi_kalman_R         = 1.9

# Kalman filter for positioning configuration
POSITION_KALMAN       = True
position_kalman_dt    = 0.2
position_kalman_dim_x = 6
position_kalman_dim_z = 3
position_kalman_x     = np.array([1, 0, 1, 0, 1, 0]).T

position_kalman_F     = np.array([[1, position_kalman_dt, 0, 0,                   0, 0], 
                                  [0, 1,                  0, 0,                   0, 0], 
                                  [0, 0,                  1, position_kalman_dt,  0, 0],
                                  [0, 0,                  0, 1,                   0, 0],
                                  [0, 0,                  0, 0,                   1, position_kalman_dt],
                                  [0, 0,                  0, 0,                   0, 1]])

position_kalman_H     = np.array([[1, 0, 0, 0, 0, 0],
                                  [0, 0, 1, 0, 0, 0],
                                  [0, 0, 0, 0, 1, 0]])

position_kalman_P     = np.eye(6) * 10

position_kalman_Q     = np.array([[0.1,  0.1, 0,   0,   0,   0],
                                  [0.1,  0.1, 0,   0,   0,   0],
                                  [0,    0,   0,   0.1, 0,   0],
                                  [0,    0,   0.1, 0.1, 0,   0],
                                  [0,    0,   0,   0,   0.1, 0.1],
                                  [0,    0,   0,   0,   0.1, 0.1]])

#position_kalman_Q     = np.eye(6) * 100.1

#position_kalman_R     = np.array([[0.005,   -0.006,   0.02],
#                                  [-0.006,  0.02,    -0.03],
#                                  [0.02,   -0.03,   0.01]])

position_kalman_R = np.eye(3) * 4

# 
labelLength = len(label)
settings = "{ \"numberOfNodes\" : %d, \"numberOfIterations\" : %d, \"logDistanceStdDev\" : %f, \"logDistanceN\" : %f, \"logDistanceRssiD0\" : %f , \"logDistanceD0\" : %f , \"bounds\" : %s}" % (numberOfNodesToUse, numberOfIterations, log_d_st_dev, log_d_n, rssi_d0, d0, multiBounds)

# Set up DB connection
conn = pymysql.connect(host = 'localhost', user = 'root', passwd = 'admin', db = 'positioning', port = 3306, cursorclass = pymysql.cursors.DictCursor)

# prepare a cursor object using cursor() method
cursor = conn.cursor()
print("Connected to database")
initial = True
# Helper functions
def selectChannelData(data):
  cArr = data['Channel']

  rArr = data['RSSI']
  nArr = data['Node_position']
  tArr = data['True_tag_position']
  
  i = rArr.idxmax()
  rssi = rArr[i] #np.mean(rArr) #
  channel = cArr[i]
  nodePosition = eval(nArr[i])
  if tArr[i] != 'NULL':
    trueTagPosition = eval(tArr[i])
  else:
    trueTagPosition = None

  return (rssi, channel, nodePosition, trueTagPosition) 


def selectiveLogDistanceParameters(channel, rssi):

  if USE_ALT_METHOD:
    X = altMethodParams[channel]["X"]
    n = altMethodParams[channel]["n"]
    return distance.altMethod(rssi=rssi, X=X, n=n)
  else:
    A = logDistanceParams[channel]["A"]
    n = logDistanceParams[channel]["n"]
    return distance.logDistancePathLoss(rssi=rssi, rssi_d0=A, d0=1.0, n=n, stDev=log_d_st_dev)


def resetFigure():
  ax.cla()
  ax.set_xlim(xaxis)
  ax.set_ylim(yaxis)
  ax.xaxis.set_major_locator(plt.MultipleLocator(1))
  ax.yaxis.set_major_locator(plt.MultipleLocator(1))
  plt.title(title)
  ax.grid(b=True, which='major', color='k', alpha=0.2, linestyle='-')
  ax.grid(b=True, which='minor', color='k', alpha=0.1, linestyle='--')
  ax.grid(color='#cccccc', linestyle='-', linewidth=1)
  ax.minorticks_on()
  ax.set_aspect(1)
  plt.rc('text', usetex=True)
  plt.rc('font', family='serif')

def rmse(a, b, dimensions=2):
  if dimensions == 2:
    return np.sqrt(np.mean([(a[i][0]-b[i][0])**2 + (a[i][1]-b[i][1])**2 for i in range(0, len(a))] ))
  elif dimensions == 3:
    return np.sqrt(np.mean([(a[i][0]-b[i][0])**2 + (a[i][1]-b[i][1])**2 + (a[i][2]-b[i][2])**2 for i in range(0, len(a))] ))

def mae(a, b, dimensions=2):
  if dimensions == 2:
    return np.mean([np.abs(np.sqrt((a[i][0]-b[i][0])**2 + (a[i][1]-b[i][1])**2)) for i in range(0, len(a)) ])
  elif dimensions == 3:
    return np.mean([np.abs(np.sqrt((a[i][0]-b[i][0])**2 + (a[i][1]-b[i][1])**2 + (a[i][2]-b[i][2])**2)) for i in range(0, len(a)) ])

def calcError(a, b, dimensions=2):
  if dimensions == 2:
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
  elif dimensions == 3:
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

# Find matching labels
selection =  "Label, COUNT(ID) AS 'numberOf', Address, MIN(Counter) AS 'minCounter'"
labelQuery = "SELECT %s FROM %s WHERE CRC LIKE 1 AND LPE LIKE 0 AND LEFT(Label, %d) LIKE LEFT('%s', %d) AND LEFT(True_tag_position, 1) LIKE '('  GROUP BY Label HAVING numberOf > 50" % (selection, tableName, labelLength, label, labelLength)
if tableName == "position_moving_testing":
  labelQuery = labelQuery = "SELECT %s FROM %s WHERE CRC LIKE 1 AND LPE LIKE 0 AND LEFT(Label, %d) LIKE LEFT('%s', %d) GROUP BY Label, Address HAVING numberOf > 50" % (selection, tableName, labelLength, label, labelLength)


labelsDataSet = pd.read_sql(labelQuery, conn)
labels = labelsDataSet['Label']

selection =  "Label, DateTime, NodeID, Address, Counter, Channel, RSSI, Node_position, True_tag_position"
q = "SELECT %s FROM %s WHERE CRC LIKE 1 AND LPE LIKE 0 AND LEFT(Label, %d) LIKE LEFT('%s', %d) AND LEFT(True_tag_position, 1) LIKE '(' ORDER BY Counter ASC LIMIT %d" % (selection, tableName, labelLength, label, labelLength, limit)

if tableName == "position_moving_testing":
  q = "SELECT %s FROM %s WHERE CRC LIKE 1 AND LPE LIKE 0 AND LEFT(Label, %d) LIKE LEFT('%s', %d) ORDER BY Counter ASC LIMIT %d" % (selection, tableName, labelLength, label, labelLength, limit)


if GET_DATA_FROM_DB:
  rowsDataSet = pd.read_sql(q, conn)
  rowsDataSet.to_pickle('Data_dumps/' + pickleDumpFolder) 
elif GET_DATA_FROM_FILE:
  rowsDataSet = pd.read_pickle('Data_dumps/' + pickleDumpFolder) 

if PLOT_ENABLED:
  import matplotlib.pyplot as plt
  plt.ion()
  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.cla()
  ax.set_xlim(xaxis)
  ax.set_ylim(yaxis)
  plt.grid()

  ax.set_aspect(1)
  ax.grid(color='#cccccc', linestyle='-', linewidth=1)

csvFolderPostfix = ""
#for A in range(-36, -34):
#  rssi_d0 = A
#  for k in np.arange(2.0, 2.2, 0.1):
#    log_d_n = k
#    csvFolderPostfix = ("%d_%.1f" % (rssi_d0, log_d_n)).replace('.', '_')
itCounter = 0

for _, record in labelsDataSet.iterrows():
  itCounter += 1
  trueTagPosition = None

  counterLimit = numberOfIterations
  tagAddress = record['Address']
  selection =  "Label, DateTime, NodeID, Address, Counter, Channel, RSSI, Node_position, True_tag_position"
  label = record['Label']
  labelLength = len(label)

  limit = 3 * maxNumberOfNodes * counterLimit

  res = rowsDataSet.loc[(rowsDataSet['Label'] == label) & (rowsDataSet['Address'] == tagAddress)].head(limit)

  counters = res.Counter.unique()
  positionEstimates = list()
  rawPositionEstimates = list()
  filteredPositions = list()
  trueTagPositions = list()
  nodes = dict()
  currentTag = Tag(tagAddress)
  if POSITION_KALMAN:
    currentPosition = Position(x=0, y=0, z=0)
    currentPosition.enableKalman(x=position_kalman_x, F=position_kalman_F, H=position_kalman_H, P=position_kalman_P, R=position_kalman_R, Q=position_kalman_Q, dim_x=position_kalman_dim_x, dim_z=position_kalman_dim_z)
  
  for nodeID in res.NodeID.unique():
    nodes[nodeID] = Node(nodeID)
    nodes[nodeID].addTag(currentTag.address)
    nodes[nodeID].tags[currentTag.address].setKalmanX(rssi_kalman_x)
    nodes[nodeID].tags[currentTag.address].setKalmanQ(rssi_kalman_Q)
    nodes[nodeID].tags[currentTag.address].setKalmanR(rssi_kalman_R)
    pos = np.array(res.loc[res.NodeID == nodeID]['Node_position'])[0]
    nodes[nodeID].setPosition(eval(pos))

  for i in range(0, min(len(counters), numberOfIterations)):
    currentCounter = counters[i]

    data = res.loc[res.Counter == currentCounter]
    rssis = list()
    channels = list()
    rawRssis = list()
    nodePositions = list()

    for nodeID, node in nodes.items():
      d = data.loc[data['NodeID'] == nodeID]
      if len(d) < 1:
        continue
      [rawRssi, channel, nodePosition, trueTagPosition] = selectChannelData(d)
      if tableName == "position_moving_testing":
        trueTagPosition = None
      rawRssis.append(rawRssi)
      nodePositions.append(nodePosition)
      channels.append(channel)

      # Kalman filtering of RSSI
      if USE_RSSI_FILTER:
        nodes[nodeID].tags[currentTag.address].kalman.predict()
        nodes[nodeID].tags[currentTag.address].kalman.update(rawRssi)
        filteredRssi = nodes[nodeID].tags[currentTag.address].kalman.x[0]
        nodes[nodeID].tags[currentTag.address].filteredRssi = filteredRssi   
        rssis.append(filteredRssi)
      else: 
        rssis.append(rawRssi)


    if len(rssis) < maxNumberOfNodes:
      continue

    # Estimate distances and multilateration
    if numberOfNodesToUse < maxNumberOfNodes:
      pData = [(nodePositions[i][0], nodePositions[i][1], nodePositions[i][2], rssis[i], channels[i]) for i in range(0, len(rssis))]
      pData.sort(key=itemgetter(3), reverse=True)
      rssis = [pData[i][3] for i in range(len(rssis))]
      channels = [pData[i][4] for i in range(len(channels))]

    if SELECTIVE_PL_PARAMS:
      distanceEstimates = [selectiveLogDistanceParameters(channels[i], rssis[i]) for i in range(len(rssis))]
    else:
      if USE_ALT_METHOD:
        distanceEstimates = [distance.altMethod(rssi=rssi, X=altMethodX, n=altMethodN) for rssi in rssis]
      else:
        distanceEstimates = [distance.logDistancePathLoss(rssi, rssi_d0, d0, log_d_n, log_d_st_dev) for rssi in rssis]

    if numberOfNodesToUse < maxNumberOfNodes:
      pData = [(pData[i][0], pData[i][1], pData[i][2], distanceEstimates[i]) for i in range(0, len(distanceEstimates))]
    else:
      pData = [(nodePositions[i][0], nodePositions[i][1], nodePositions[i][2], distanceEstimates[i]) for i in range(0, len(distanceEstimates))]
    positionEstimate = multi.multilateration(pData[:numberOfNodesToUse], startingPoint=multiStartingPoint, plotEnabled=False, dimensions=3, bounds=multiBounds)
    

    if not ONLY_FILTERED:
      rawDistanceEstimates = [distance.logDistancePathLoss(rssi, rssi_d0, d0, log_d_n, log_d_st_dev) for rssi in rawRssis]
      rawPData = [(nodePositions[i][0], nodePositions[i][1], nodePositions[i][2], rawDistanceEstimates[i]) for i in range(0, len(rawDistanceEstimates))]
      rawPositionEstimate = multi.multilateration(rawPData, plotEnabled=False, dimensions=3, bounds=multiBounds, startingPoint=multiStartingPoint)

    if initial:
      initial = False
      currentPosition.setKalmanX(np.array([positionEstimate[0], 0, positionEstimate[1], 0, positionEstimate[2], 0]))

    filteredPosition = currentPosition.updatePosition((positionEstimate[0], positionEstimate[1], positionEstimate[2]))

    if not ONLY_FILTERED:
      rawPositionEstimates.append(rawPositionEstimate)
      positionEstimates.append(positionEstimate)
    filteredPositions.append(filteredPosition)
    trueTagPositions.append(trueTagPosition)


    if (trueTagPosition != None) and (type(trueTagPosition) != 'float') and not ONLY_FILTERED:
      error2d = calcError(positionEstimate, trueTagPosition, dimensions=2)
      error3d = calcError(positionEstimate, trueTagPosition, dimensions=3)

    if PLOT_ENABLED:
      resetFigure()
      #ax.text(6, 3, ''.join(("Error 2D: ", str(round(error2d, 2)))))
      #ax.text(6, 1, ''.join(("Error 3D: ", str(round(error3d, 2)))))

      # Plot node positions with respective radius estimate
      circles = [plt.Circle((nodePositions[i][0], nodePositions[i][1]), radius=distanceEstimates[i], color=radiusColor, alpha=0.1) for i in range(0, len(distanceEstimates))]
      [ax.add_patch(circle) for circle in circles]

      centers = [plt.Circle((nodePositions[i][0], nodePositions[i][1]), radius=nodePositionDotRadius, color=nodePositionColor, alpha=1) for i in range(0, len(distanceEstimates))]
      [ax.add_patch(center) for center in centers]

      if not ONLY_FILTERED:
        # Plot estimated position indicator using raw RSSIs and no position filter
        rawPositionIndicator = plt.Circle(rawPositionEstimate, radius=tagPositionDotRadius, color=rawTagColor, alpha=1)
        ax.add_patch(rawPositionIndicator)

        # Plot estimated position indicator using Kalman filtered RSSIs
        positionIndicator = plt.Circle(positionEstimate, radius=tagPositionDotRadius, color=tagColor, alpha=1)
        ax.add_patch(positionIndicator)

      # Plot filtered position indicator
      filteredPositionIndicator = plt.Circle(filteredPosition, radius=tagPositionDotRadius, color=kalmanTagColor, alpha=1)
      ax.add_patch(filteredPositionIndicator)

      # Plot true tag position
      if trueTagPosition != None and type(trueTagPosition) != 'float':
        truePositionIndicator = plt.Circle(trueTagPosition, radius=tagPositionDotRadius, color=truePositionColor, alpha=1)
        ax.add_patch(truePositionIndicator)

      plt.draw()
      plt.pause(0.0001)

  # Calculate erors with regards to true position
  if (trueTagPosition != None) and (type(trueTagPosition) != 'float'):  
    if not ONLY_FILTERED:
      rmse2d = rmse(positionEstimates, trueTagPositions, dimensions=2)
      rmse3d = rmse(positionEstimates, trueTagPositions, dimensions=3)
      mae2d = mae(positionEstimates, trueTagPositions, dimensions=2)
      mae3d = mae(positionEstimates, trueTagPositions, dimensions=3)

      filtered_rmse2d = rmse(filteredPositions, trueTagPositions, dimensions=2)
      filtered_rmse3d = rmse(filteredPositions, trueTagPositions, dimensions=3)
      filtered_mae2d = mae(filteredPositions, trueTagPositions, dimensions=2)
      filtered_mae3d = mae(filteredPositions, trueTagPositions, dimensions=3)

    print("Label number %d: %s" % (itCounter, label))
    print("A = %.1f, n = %.2f" % (rssi_d0, log_d_n))

    if not ONLY_FILTERED:
      print("Information on label: ", label)
      print(("RMSE-2D: \t%f" % rmse2d).replace('.', ','))
      print(("MAE-2D: \t%f" % mae2d).replace('.', ','))
      print(("RMSE-3D: \t%f" % rmse3d).replace('.', ','))
      print(("MAE-3D: \t%f" % mae3d).replace('.', ','))
      print("")
      print(("Filtered RMSE-2D: \t%f" % filtered_rmse2d).replace('.', ','))
      print(("Filtered MAE-2D: \t%f" % filtered_mae2d).replace('.', ','))
      print(("Filtered RMSE-3D: \t%f" % filtered_rmse3d).replace('.', ','))
      print(("Filtered MAE-3D: \t%f" % filtered_mae3d).replace('.', ','))
      print("")

  if not ONLY_FILTERED:
    positionX = [a[0] for a in positionEstimates]
    positionY = [a[1] for a in positionEstimates]
    positionZ = [a[2] for a in positionEstimates]
    filteredX = [a[0] for a in filteredPositions]
    filteredY = [a[1] for a in filteredPositions]
    filteredZ = [a[2] for a in filteredPositions]
    rawX = [a[0] for a in rawPositionEstimates]
    rawY = [a[1] for a in rawPositionEstimates]
    rawZ = [a[2] for a in rawPositionEstimates]

    if PLOT_ENABLED:
      plt.plot(rawX, rawY, color=rawTagColor)
      plt.plot(positionX, positionY, color=tagColor)
      plt.plot(filteredX[10:], filteredY[10:], color=kalmanTagColor)
      positionfilteredYndicator = plt.Circle(positionEstimate, radius=tagPositionDotRadius, color=tagColor, alpha=1)
      positionIndicator = plt.Circle(filteredPosition, radius=tagPositionDotRadius, color=kalmanTagColor, alpha=1)
      ax.add_patch(positionIndicator)
      plt.draw()
      plt.pause(0.0001)

      if trueTagPosition != None and type(trueTagPosition) != 'float':
        txt = "\\textbf{RMSE: %.2fm, MAE: %.2fm}" % (rmse2d, mae2d)
        plt.annotate(txt, (0,0), (0, -30), xycoords='axes fraction', textcoords='offset points', va='top')

      c1 = np.cov(positionX, positionY)
      c2 = np.cov(positionX, positionZ)
      c3 = np.cov(positionY, positionZ)

      print("Data for label: ", label)
      print("Variance raw X:", np.var(positionX))
      print("Variance raw Y:", np.var(positionY))
      #print("Covariances: ", c1, c2, c3)
      print("Variance filtered X:", np.var(filteredX))
      print("Variance filtered Y:", np.var(filteredY))
      input("")

  if SAVE_TO_CSV:
    if USE_WINDOWS:
      path = 'C:\\Users\\jagu\\Dropbox\\Elektro\\Kyb\Master\\Results\\Scripts\\data\\%s_%s\\' % (csvFolderPrefix, csvFolderPostfix)
    else:
      path = '/Users/jantoreguggedal/Dropbox/Elektro/Kyb/Master/Results/Scripts/data/%s_%s/' % (csvFolderPrefix, csvFolderPostfix)
    if not os.path.exists(path):
      os.makedirs(path)
    prefix = "%d - " % (itCounter)
    filename = "%s%sUnfiltered.csv" % (path, prefix)
    np.savetxt(filename, positionEstimates, delimiter=',')
    filename = "%s%sRaw.csv" % (path, prefix)
    np.savetxt(filename, rawPositionEstimates, delimiter=',')
    filename = "%s%sFiltered.csv" % (path, prefix)
    np.savetxt(filename, filteredPositions, delimiter=',')
    filename = "%s%sNode_positions.csv" % (path, prefix)
    np.savetxt(filename, nodePositions, delimiter=',')
    if tableName != "position_moving_testing":
      filename = "%s%sTrue_position.csv" % (path, prefix)
      np.savetxt(filename, trueTagPosition, delimiter=',')
    filename = "%s%sLabel.csv" % (path, prefix)
    np.savetxt(filename, np.array([label]), fmt='%s', delimiter=',')
    filename = "%s%sSettings.csv" % (path, prefix)
    np.savetxt(filename, np.array([settings]), fmt='%s', delimiter=',')


