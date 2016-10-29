import sys
from itertools import chain

file_in = sys.argv[1]
file_out = sys.argv[2]
 
grouped = dict()

with open(file_in) as file:
    next(file)
    for ln in file:
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

with open(file_out, 'w+') as file:
    file.write('date,pickup_longitude,pickup_latitude,rides,total_fare\n')
    for key, value in grouped.iteritems():
        file.write(','.join(str(x) for x in chain(key, value)) + '\n')
