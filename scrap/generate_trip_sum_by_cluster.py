import os
from sklearn.cluster import MiniBatchKMeans
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

# Process all of the files in the source directory, creating pickup and dropoff lat/long and dates
pickup_points = list()
dropoff_points = list()
dates = list()
for filename in os.listdir('taxi-data/2015'):
    with open(os.path.join('taxi-data/2015', filename)) as file:
        next(file)
        for ln in file:
            row = ln.strip().split(',')
            date = row[1].split(' ')[0]
            long = float(row[5])
            lat = float(row[6])
            longd = float(row[9])
            latd = float(row[10])
            if long != 0 and lat != 0:
                pickup_points.append((lat, long))                
                dropoff_points.append((latd, longd))
                dates.append(date)

# Concatenate the pickup and dropoff into a single array to do the cluster fit
pickup_points = np.array(pickup_points)
dropoff_points = np.array(dropoff_points)
dates = np.array(dates)
all_points = np.concatenate((pickup_points, dropoff_points), axis=0)
# delete intermediary arrays to save memory
del pickup_points
del dropoff_points

# Perform the cluster fit
n_clusters = 30
kmeans = MiniBatchKMeans(n_clusters=n_clusters).fit(all_points)

labels = kmeans.labels_
unique_labels = set(labels)

cluster_centers = kmeans.cluster_centers_

# transform the pickup and dropoff data with the clusters identified back into an array 
# that will look like this:
#  Date, Pickup lat, Pickup long, pickup cluster label, dropoff lat, dropoff long, dropoff cluster label
labels = labels.reshape(labels.size, 1)
points_and_labels = np.concatenate((all_points, labels), 1)
pickup_pandl = points_and_labels[0:dates.size]
dropoff_pandl = points_and_labels[dates.size:]
dates = dates.reshape(dates.size,1)
del labels
del points_and_labels
taxi_cluster_raw = np.concatenate((dates, pickup_pandl, dropoff_pandl), 1)
del pickup_pandl
del dropoff_pandl

# Save off a copy of the raw data after clustering
np.savetxt("out/taxi_cluster_raw.csv", taxi_cluster_raw, delimiter=",", fmt='%s')


# NOTE: There has to be a better way of doing this next step, but this worked
#
# Create a list of keys (date, pickup cluster label, dropoff cluster label) to use
# to do a unique count
keys = list()
for i in range(0,taxi_cluster_raw.size/7):
     newkey = taxi_cluster_raw[i,0] + ',' + taxi_cluster_raw[i,3] + ',' + taxi_cluster_raw[i,6]
     keys.append(newkey)
keys = np.array(keys)

# generate a ilst of unique keys and counts
taxi_cluster_u, taxi_cluster_c = np.unique(keys, return_counts=True)

# concatenate results into single array for easy output
taxi_cluster_u = np.array(taxi_cluster_u).reshape(taxi_cluster_u.size,1)
taxi_cluster_c = np.array(taxi_cluster_c).reshape(taxi_cluster_c.size,1)
taxi_cluster_sum = np.concatenate((taxi_cluster_u,taxi_cluster_c), 1)

# Save final output
np.savetxt("out/taxi_cluster_sum.csv", taxi_cluster_sum, delimiter=",", fmt='%s')
