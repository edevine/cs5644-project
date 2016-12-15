from sklearn.cluster import DBSCAN
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.spatial import ConvexHull

points = list()

with open('../taxi-data/yellow_tripdata_2015-01.csv') as file:
    i = 0
    next(file)
    for ln in file:
        i += 1
        # test on the first 10000. The whole file runs out of memory
        if i > 10000:
            break
        row = ln.strip().split(',')
        long = float(row[5])
        lat = float(row[6])
        if long != 0 and lat != 0:
            points.append((lat, long))

points = np.array(points)

db = DBSCAN(eps=0.005, min_samples=10, metric='haversine', p=None).fit(points)

labels = db.labels_
unique_labels = set(labels) - set([-1])

num_clusters = len(unique_labels)
colors = plt.cm.Spectral(np.linspace(0, 1, num_clusters))

for label, color in zip(unique_labels, colors):
    cluster = points[labels == label]

    hull = ConvexHull(cluster)
    vertices = np.append(hull.vertices, hull.vertices[0])

    plt.fill(cluster[vertices,1], cluster[vertices,0], color=color, alpha = 0.5)
    plt.plot(cluster[vertices,1], cluster[vertices,0], '-', color=color, lw=1, fillstyle='full')

    plt.plot(cluster[:, 1], cluster[:, 0], 'o', markerfacecolor=color, markeredgecolor='k', markersize=6)


plt.title('DBSCAN estimated clusters: %d' % num_clusters)
plt.show()
