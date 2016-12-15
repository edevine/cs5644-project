import os
import json
from sklearn.cluster import MiniBatchKMeans
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.spatial import ConvexHull

with open('geo-data/borough-boundaries.json') as file:
    boroBoundaries = json.load(file)

boros = boroBoundaries['features']
colors = plt.cm.Spectral(np.linspace(0, 1, len(boros)))

# Draw map
for boro in boros:
    for shape in boro['geometry']['coordinates']:
        for line in shape:
            x = [pt[0] for pt in line]
            y = [pt[1] for pt in line]
            plt.fill(x, y, color='black', alpha=0.3)
            plt.plot(x, y, '-', color='black', lw=1)

# Read taxi data
points = list()
for filename in os.listdir('taxi-data'):
    with open(os.path.join('taxi-data', filename)) as file:
        next(file)
        for ln in file:
            row = ln.strip().split(',')
            long = float(row[5])
            lat = float(row[6])
            if long != 0 and lat != 0:
                points.append((lat, long))

points = np.array(points)

# Cluster taxi data
n_clusters = 30
kmeans = MiniBatchKMeans(n_clusters=n_clusters).fit(points)

labels = kmeans.labels_
unique_labels = set(labels)

cluster_centers = kmeans.cluster_centers_

# Plot taxi points
colors = plt.cm.Spectral(np.linspace(0, 1, n_clusters))

for label, color in zip(unique_labels, colors):
    cluster = points[labels == label]
    center = cluster_centers[label]

    hull = ConvexHull(cluster)
    vertices = np.append(hull.vertices, hull.vertices[0])


    plt.fill(cluster[vertices,1], cluster[vertices,0], color=color, alpha = 0.5)
    plt.plot(cluster[vertices,1], cluster[vertices,0], '-', color=color, lw=1)

    plt.plot(center[1], center[0], 'o', markerfacecolor=color, markeredgecolor='black', markersize=6)
    #plt.plot(cluster[:, 1], cluster[:, 0], 'o', markerfacecolor=color, markeredgecolor='black', markersize=6)

# TODO: Remove outliers
plt.axis((-74.3,-73.7,40.5,40.9))
plt.title('Mini Batch K-Means estimated clusters: %d' % n_clusters)
plt.show()
