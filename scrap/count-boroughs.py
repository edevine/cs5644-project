import sys
import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection
import numpy as np
from scipy.spatial import ConvexHull

try:
    magnitude = int(sys.argv[1])
except:
    magnitude = 3

resolution = 10**magnitude

# Sort Boroughs by expected occurances (desc):
keyDict = {
    'Manhattan': 0,
    'Queens': 1,
    'Brooklyn': 2,
    'Bronx': 3,
    'Staten Island': 4
}
def toBoroKey(boro):
    return keyDict[boro.name]

def toPathLen(path):
    return len(path.vertices)

class Borough:
    def __init__(self, name, geoCoord):
        self.name = name
        self.lowResPaths = []
        self.geoCoord = geoCoord
        for shape in geoCoord:
            for line in shape:
                # Ignore small line segments
                if len(line) >= 200:
                    self.lowResPaths.append(Path(line[::20]))
        # Sort by path length desc
        self.lowResPaths.sort(key=toPathLen, reverse=True)
    
    def inLowResPath(self, point):
        for path in self.lowResPaths:
            if (path.contains_point(point)):
                return True
        return False

def toBorough(feature):
    return Borough(feature['properties']['BoroName'], feature['geometry']['coordinates'])

with open('geo-data/borough-boundaries.json') as file:
    boroBoundaries = json.load(file)

boros = map(toBorough, boroBoundaries['features'])
boros.sort(key=toBoroKey)
borosPickupPoints = [[] for _ in boros]
borosDropoffPoints = [[] for _ in boros]
notFoundPickupPoints = []
notFoundDropoffPoints = []
handles = []
colors = plt.cm.Spectral(np.linspace(0, 1, len(boros)))

def find_boro(point):
    if point[0] == 0 or point[1] == 0:
        return -1
    for [i, boro] in enumerate(boros):
        if (boro.inLowResPath(point)):
            return i
    return -1

lineCount = 0
for filename in os.listdir('taxi-data/2015'):
    with open(os.path.join('taxi-data/2015', filename)) as file:
        next(file)
        for ln in file:
            if lineCount % resolution == 0:
                row = ln.strip().split(',')

                pickup = (float(row[5]), float(row[6]))
                i = find_boro(pickup)
                if i != -1:
                    borosPickupPoints[i].append(pickup)
                else:
                    notFoundPickupPoints.append(pickup)
                
                dropoff = (float(row[9]), float(row[10]))
                i = find_boro(dropoff)
                if i != -1:
                    borosDropoffPoints[i].append(dropoff)
                else:
                    notFoundDropoffPoints.append(dropoff)

            lineCount += 1

# Draw map
for [boro, color] in zip(boros, colors):
    for shape in boro.geoCoord:
        for line in shape:
            x, y = zip(*line)
            plt.fill(x, y, color=color, alpha = 0.5)
            plt.plot(x, y, '-', color=color, lw=1)

# Draw detection paths
for [boro, color] in zip(boros, colors):
    for path in boro.lowResPaths:
        x, y = zip(*path.vertices)
        plt.plot(x, y, '--', color='black', lw=2)

# Draw points
for [points, color] in zip(borosPickupPoints, colors):
    if len(points) > 0:
        x, y = zip(*points)
        plt.plot(x, y, 'o', markerfacecolor=color, markeredgecolor='black', markersize=4)

for [points, color] in zip(borosDropoffPoints, colors):
    if len(points) > 0:
        x, y = zip(*points)
        plt.plot(x, y, '*', markerfacecolor=color, markeredgecolor='black', markersize=4)

# Draw not found points
x, y = zip(*notFoundPickupPoints)
plt.plot(x, y, 'o', markerfacecolor='red', markeredgecolor='red', markersize=6)
x, y = zip(*notFoundDropoffPoints)
plt.plot(x, y, '*', markerfacecolor='red', markeredgecolor='red', markersize=6)

# Draw legend
for [boro, points, color] in zip(boros, borosPickupPoints, colors):
    count = len(points)
    if magnitude == 0:
        label = boro.name + ' (' + str(count) + ')'
    else:
        label = boro.name + ' (' + str(count) + 'e' + str(magnitude) + ')'
        
    handles.append(mpatches.Patch(color=color, label=label))
    print label

if magnitude == 0:
    notFoundLabel = 'Not found (' + str(len(notFoundPickupPoints)) + ')'
else:
    notFoundLabel = 'Not found (' + str(len(notFoundPickupPoints)) + 'e' + str(magnitude) + ')'

handles.append(Line2D([], [], linestyle='-', color='red', marker='o', markeredgecolor='red', label=notFoundLabel, linewidth=0))
print notFoundLabel

plt.axis((-74.3,-73.7,40.5,40.9))
plt.legend(loc='upper left', handles=handles)
plt.title('Taxi Pickup Locations. (Point = ' + str(resolution) + ')')
plt.show()
