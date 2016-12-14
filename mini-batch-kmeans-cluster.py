from sklearn.cluster import MiniBatchKMeans
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

points = list()

with open('taxi-data/yellow_tripdata_2015-01.csv') as file:
    next(file)
    for ln in file:
        row = ln.strip().split(',')
        long = float(row[5])
        lat = float(row[6])
        if long != 0 and lat != 0:
            points.append((lat, long))

points = np.array(points)

n_clusters = 30
kmeans = MiniBatchKMeans(n_clusters=n_clusters).fit(points)

labels = kmeans.labels_
unique_labels = set(labels)

colors = plt.cm.Spectral(np.linspace(0, 1, n_clusters))

for label, color in zip(unique_labels, colors):
    cluster = points[labels == label]

    hull = ConvexHull(cluster)
    vertices = np.append(hull.vertices, hull.vertices[0])

    plt.fill(cluster[vertices,1], cluster[vertices,0], color=color, alpha = 0.5)
    plt.plot(cluster[vertices,1], cluster[vertices,0], '-', color=color, lw=1, fillstyle='full')

    plt.plot(cluster[:, 1], cluster[:, 0], 'o', markerfacecolor=color, markeredgecolor='k', markersize=6)

# TODO: Remove outliers
plt.axis((-74.1,-73.7,40.6,40.9))
plt.title('Mini Batch K-Means estimated clusters: %d' % n_clusters)
plt.show()
