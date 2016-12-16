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
from collections import namedtuple
import csv

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
        self.key = keyDict[name]
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
    def __init__(self, center, records):
        self.center = center
        self.records = records

class Record:
    def __init__(self, date, boroName, fare, pickup):
        self.boroName = boroName
        self.date = date
        self.fare = fare
        self.pickup = pickup

def toBorough(feature):
    return Borough(feature['properties']['BoroName'], feature['geometry']['coordinates'])

with open('geo-data/borough-boundaries.json') as file:
    boroBoundaries = json.load(file)

boros = map(toBorough, boroBoundaries['features'])
boros.sort(key=toBoroKey)
boros.pop()
boroRecords = dict()
for boro in boros:
    boroRecords[boro.name] = []

def find_boro(point):
    if point[0] == 0 or point[1] == 0:
        return None
    for boro in boros:
        if (boro.inLowResPath(point)):
            return boro.name
    return None

# Read taxi data
lineCount = 0
for filename in os.listdir('taxi-data/2015'):
    with open(os.path.join('taxi-data/2015', filename)) as file:
        next(file)
        for ln in file:
            if lineCount % resolution == 0:
                row = ln.strip().split(',')
                date = row[1].split(' ')[0]
                long = round(float(row[5]), 3)
                lat = round(float(row[6]), 3)
                fare = float(row[18])
                pickup = (long, lat)
                
                boro_name = find_boro(pickup)
                if boro_name is not None:
                    record = Record(date, boro_name, fare, (long, lat))
                    boroRecords[boro_name].append(record)
            lineCount += 1

# Compute clusters
totalRecords = sum(len(boroRecords[name]) for name in boroRecords)
clusters = []
for boro in boros:
    records = boroRecords[boro.name]
    if (len(records) <= 2): continue

    boro_n_clusters = int(round((float(len(records)) / totalRecords) * n_clusters))

    if boro_n_clusters < 2:
        boro_n_clusters = 2
    
    points = [record.pickup for record in records]

    kmeans = MiniBatchKMeans(n_clusters=boro_n_clusters).fit(points)
    cluster_centers = kmeans.cluster_centers_
    labels = kmeans.labels_
    cluster_labels = set(labels)

    for cluster_label in cluster_labels:
        cluster_records = []
        for [i, label] in enumerate(labels):
            if label == cluster_label:
                cluster_records.append(records[i])

        center = cluster_centers[label]

        clusters.append(Cluster((center[0], center[1]), cluster_records))

# Draw map
for boro in boros:
    for shape in boro.geoCoord:
        for line in shape:
            x, y = zip(*line)
            plt.fill(x, y, color='black', alpha=0.2)
            plt.plot(x, y, '-', color='black', lw=1)

# Draw clusters
colors = plt.cm.Spectral(np.linspace(0, 1, len(clusters)))

for [cluster, color] in zip(clusters, colors):
    cluster_points = [record.pickup for record in cluster.records]
    try:
        hull = ConvexHull(cluster_points)
        
        hull_points = [cluster_points[i] for i in hull.vertices]
        hull_points.append(hull_points[0])
        x, y = zip(*hull_points)
        plt.fill(x, y, color=color, alpha=0.5)
        plt.plot(x, y, '-', color=color, lw=1)
    except:
        print 'Could not run ConvexHull'

    x, y = zip(*cluster_points)
    plt.plot(x, y, 'o', markerfacecolor=color, markeredgecolor='black', markersize=4)

# Sum clusters
grouped_records = dict()
for cluster in clusters:
    for record in cluster.records:
        key = (record.date, record.boroName, cluster.center)
        if key not in grouped_records:
            grouped_records[key] = (record.fare, 1)
        else:
            fare = grouped_records[key][0] + record.fare
            count = grouped_records[key][1] + 1
            grouped_records[key] = (fare, count)

file_lines = []
for key in grouped_records:
    value = grouped_records[key]
    file_lines.append([key[0], key[1], str(key[2][0]), str(key[2][1]), str(value[0]), str(value[1] * resolution)])

file_lines.sort(key=lambda line: line[0])

with open('out/clustered_taxi_data.csv', 'w+') as file:
    header = ['Date', 'Borough', 'Long', 'Lat', 'Fare', 'Count']
    file.write(','.join(header) + '\n')
    for line in file_lines:
        file.write(', '.join(line) + '\n')

plt.title('Taxi Pickup Locations. (Point = ' + str(resolution) + ')')
plt.show()
