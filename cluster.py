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
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_
unique_labels = set(labels)
num_clusters = len(unique_labels) - (1 if -1 in labels else 0)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = 'k'

    class_member_mask = (labels == k)

    xy = points[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)

    xy = points[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % num_clusters)
plt.show()