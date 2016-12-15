import sys
import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from scipy.spatial import ConvexHull

import warnings
warnings.filterwarnings("ignore")

try:
    magnitude = int(sys.argv[1])
except:
    magnitude = 3

try:
    n_clusters = int(sys.arv[2])
except:
    n_clusters = 30

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

class Cluster:
    def __init__(self, center, points):
        self.center = center
        self.points = points

def toBorough(feature):
    return Borough(feature['properties']['BoroName'], feature['geometry']['coordinates'])

with open('geo-data/borough-boundaries.json') as file:
    boroBoundaries = json.load(file)

boros = map(toBorough, boroBoundaries['features'])
boros.sort(key=toBoroKey)
boros.pop()
borosPoints = [[] for _ in boros]

def find_boro(point):
    if point[0] == 0 or point[1] == 0:
        return -1
    for [i, boro] in enumerate(boros):
        if (boro.inLowResPath(point)):
            return i
    return -1

# Read taxi data
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
                    borosPoints[i].append(pickup)

                #dropoff = (float(row[9]), float(row[10]))
                # i = find_boro(dropoff)
                # if i != -1:
                #     borosPoints[i].append(dropoff)
                # else:
                #     notFoundPoints.append(dropoff)
            lineCount += 1

# Draw map
for boro in boros:
    for shape in boro.geoCoord:
        for line in shape:
            x, y = zip(*line)
            plt.fill(x, y, color='black', alpha=0.3)
            plt.plot(x, y, '-', color='black', lw=1)

# Draw detection paths
# for [boro, color] in zip(boros, colors):
#     for path in boro.lowResPaths:
#         x, y = zip(*path.vertices)
#         plt.plot(x, y, '--', color='black', lw=2)



totalPoints = sum(len(points) for points in borosPoints)
clusters = []
for [i, points] in enumerate(borosPoints):
    if (len(points) == 0): continue

    boro_n_clusters = int(round((float(len(points)) / totalPoints) * n_clusters))

    if boro_n_clusters < 2:
        boro_n_clusters = 2
    
    kmeans = MiniBatchKMeans(n_clusters=boro_n_clusters).fit(points)
    cluster_centers = kmeans.cluster_centers_
    labels = kmeans.labels_
    cluster_labels = set(labels)

    for cluster_label in cluster_labels:
        cluster_points = []
        for [i, label] in enumerate(labels):
            if label == cluster_label:
                cluster_points.append(points[i])

        center = cluster_centers[label]

        clusters.append(Cluster(center, cluster_points))

colors = plt.cm.Spectral(np.linspace(0, 1, len(clusters)))

for [cluster, color] in zip(clusters, colors):
    try:
        hull = ConvexHull(cluster.points)
        
        hull_points = [cluster.points[i] for i in hull.vertices]
        hull_points.append(hull_points[0])
        x, y = zip(*hull_points)
        plt.fill(x, y, color=color, alpha=0.5)
        plt.plot(x, y, '-', color=color, lw=1)
    except:
        print 'Could not run ConvexHull'

    x, y = zip(*cluster.points)
    plt.plot(x, y, 'o', markerfacecolor=color, markeredgecolor='black', markersize=4)

plt.axis((-74.1,-73.7,40.5,40.9))
plt.title('Taxi Pickup Locations. (Point = ' + str(resolution) + ')')
plt.show()
