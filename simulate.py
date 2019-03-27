import shapely.geometry as geom
import shapely.affinity as affin

import numpy as np

from matplotlib import pyplot as plt

from descartes import PolygonPatch

import math

# How many radians the inner gear rotates each step.
THETA_STEP = .1 

def add_gear_figure(poly, outer_radius, gear_name):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.add_patch(PolygonPatch(poly))

    axis_size = round(outer_radius)
    ax.axis((-axis_size, axis_size, -axis_size, axis_size))
    ax.set_title(gear_name)
    ax.set_aspect(1)

    plt.show()

def simulate(inner_teeth, outer_teeth):
    points = []
    total_rads = 0
    pencil_radius = .5*inner_teeth
    r_diff = outer_teeth - inner_teeth

    print(inner_teeth,outer_teeth)
    lcm = np.lcm(inner_teeth,outer_teeth)
    rotations = lcm/inner_teeth

    while total_rads < rotations*2*math.pi:
        x = r_diff * math.cos(total_rads) + pencil_radius * math.cos((r_diff/inner_teeth)*total_rads)
        y = r_diff * math.sin(total_rads) - pencil_radius * math.sin((r_diff/inner_teeth)*total_rads)
        points.append((x,y))
        total_rads += THETA_STEP

    line = geom.LineString(points).buffer(.01)

    add_gear_figure(line,outer_teeth,"Test")

# simulate(40,96)

