import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

import shapely.geometry as geom
import shapely.affinity as affin
from descartes import PolygonPatch

import math
import createdictionary

THETA_STEP = .1

inner_teeth = 96
outer_teeth = 144


points = 7

fig = plt.figure()
ax = fig.add_subplot(111)

axis_size = round(outer_teeth)
ax.axis((-axis_size, axis_size, -axis_size, axis_size))
ax.set_aspect(1)

axcolor = 'lightgoldenrodyellow'
axpoint = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)

spoint = Slider(axpoint, 'Point', 0.0, 1.0, valinit=0.0, valstep=0.01)



def update(val):
    pos = spoint.val
    points = []
    total_rads = 0
    pencil_radius = pos*inner_teeth
    r_diff = outer_teeth - inner_teeth

    lcm = np.lcm(inner_teeth,outer_teeth)
    rotations = lcm/inner_teeth

    while total_rads < rotations*2*math.pi:
        x = r_diff * math.cos(total_rads) + pencil_radius * math.cos((r_diff/inner_teeth)*total_rads)
        y = r_diff * math.sin(total_rads) - pencil_radius * math.sin((r_diff/inner_teeth)*total_rads)
        points.append((x,y))
        total_rads += THETA_STEP

    
    line = geom.LineString(points).buffer(.01)
    for p in ax.patches:
        p.remove()
    ax.add_patch(PolygonPatch(line))

    
    
spoint.on_changed(update)

rax = plt.axes([0.025, 0.4, 0.15, 0.3], facecolor=axcolor)

t = ()
for i in createdictionary.point_combos[points]:
    outer = i[0]
    inner = i[1]
    if len(t) < 10:
        t = t + (str(outer) + '/' + str(inner), )
    
radio = RadioButtons(rax, t, active=0)


def changecombo(label):
    global outer_teeth
    global inner_teeth
    outer_teeth, inner_teeth = label.split("/")
    outer_teeth = int(outer_teeth)
    inner_teeth = int(inner_teeth)
    update(spoint.val)
    

radio.on_clicked(changecombo)

changecombo(radio.value_selected)

plt.show()
