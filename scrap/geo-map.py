import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
from scipy.spatial import ConvexHull

with open('geo-data/borough-boundaries.json') as file:
    boroBoundaries = json.load(file)

boros = boroBoundaries['features']
colors = plt.cm.Spectral(np.linspace(0, 1, len(boros)))

handles = []

# Draw boroughs
for [boro, color] in zip(boros, colors):
    for shape in boro['geometry']['coordinates']:
        for line in shape:
            x, y = zip(*line)
            plt.fill(x, y, color=color)
            plt.plot(x, y, '-', color='black', lw=1)

            sparseLine5 = line[::5]
            x, y = zip(*sparseLine5)
            plt.plot(x, y, '-', color='blue', lw=1)

            sparseLine20 = line[::20]
            x, y = zip(*sparseLine20)
            plt.plot(x, y, '-', color='red', lw=1)

            hull = ConvexHull(line)
            hullLine = [line[i] for i in hull.vertices]
            hullLine.append(hullLine[0])
            x, y = zip(*hullLine)
            plt.plot(x, y, '--', color='red', lw=3)

# Draw legend
for [boro, color] in zip(boros, colors):
    boroName = boro['properties']['BoroName']
    handles.append(mpatches.Patch(color=color, label=boroName))

handles.append(Line2D([0], [0], linestyle='-', color='blue', label='Sparse Line (5)', linewidth=1))
handles.append(Line2D([0], [0], linestyle='-', color='red', label='Sparse Line (20)', linewidth=1))
handles.append(Line2D([0], [0], linestyle='--', color='red', label='Convex Hull', linewidth=2))

plt.legend(loc='upper left', handles=handles)

plt.show()
