import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

with open('geo-data/borough-boundaries.json') as file:
    boroBoundaries = json.load(file)

boros = boroBoundaries['features']
colors = plt.cm.Spectral(np.linspace(0, 1, len(boros)))

handles = []

for [boro, color] in zip(boros, colors):
    boroName = boro['properties']['BoroName']
    handles.append(mpatches.Patch(color=color, label=boroName))
    for shape in boro['geometry']['coordinates']:
        for line in shape:
            x = [pt[0] for pt in line]
            y = [pt[1] for pt in line]
            plt.fill(x, y, color=color)
            plt.plot(x, y, '-', color='black', lw=1)

plt.legend(loc='upper left', handles=handles)
plt.show()
