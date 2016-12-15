import sys
import os
from itertools import chain

dir_in = sys.argv[1]
file_out = sys.argv[2]
 
grouped = dict()
totalCount = 0
for filename in os.listdir(dir_in):
    print 'Processing', filename
    fileCount = 0
    with open(os.path.join(dir_in, filename)) as file:
        next(file)
        for ln in file:
            fileCount += 1
            row = ln.strip().split(',')
            date = row[1].split(' ')[0]
            long = round(float(row[5]), 3)
            lat = round(float(row[6]), 3)
            fare = float(row[18])
            key = (date, long, lat)

            if key not in grouped:
                grouped[key] = [1, fare]
            else:
                grouped[key][0] += 1
                grouped[key][1] += fare
    print 'File count', fileCount
    totalCount += fileCount

print 'Total count', totalCount

with open(file_out, 'w+') as file:
    for key, value in grouped.iteritems():
        file.write(','.join(str(x) for x in chain(key, value)) + '\n')
