from sklearn.cluster import DBSCAN
import numpy as np
import matplotlib.pyplot as plt

points = list()

with open('taxi-data/yellow_tripdata_2015-01.csv') as file:
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
    plt.plot(cluster[:, 1], cluster[:, 0], 'o', markerfacecolor=color, markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % num_clusters)
plt.show()
