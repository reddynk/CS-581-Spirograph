import shapely.geometry as geom
import shapely.affinity as affin

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

def simulate(radius_small, radius_big):
    points = []
    total_rads = 0
    pencil_radius = .5*radius_small
    r_diff = radius_big - radius_small

    print(radius_small,radius_big)

    while total_rads < 6*math.pi:
        x = r_diff * math.cos(total_rads) + pencil_radius * math.cos((r_diff/radius_small)*total_rads)
        y = r_diff * math.sin(total_rads) - pencil_radius * math.sin((r_diff/radius_small)*total_rads)
        points.append((x,y))
        total_rads += THETA_STEP

    line = geom.LineString(points).buffer(.01)

    add_gear_figure(line,radius_big,"Test")

# simulate(40,96)

