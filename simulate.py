import shapely.geometry as geom
import shapely.affinity as affin

import numpy as np

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from descartes import PolygonPatch

import math

from mayavi import mlab

# How many radians the inner gear rotates each step.
THETA_STEP = .1
# How thick the tubes of the 3d spirograph are.
TUBE_THICKNESS = 2


def show_2d_plot(poly, outer_radius, gear_name):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.add_patch(PolygonPatch(poly))

    axis_size = round(outer_radius)
    ax.axis((-axis_size, axis_size, -axis_size, axis_size))
    ax.set_title(gear_name)
    ax.set_aspect(1)

    plt.show()

def show_3d_plot(points, outer_radius, gear_name, display_3d, save_to_obj):
    black = (0,0,0)
    white = (1,1,1)
    mlab.figure(bgcolor=white)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]
    mlab.plot3d(xs,ys,zs, color=black, tube_radius=TUBE_THICKNESS)
    if save_to_obj:
        mlab.savefig(gear_name + ".obj")
    if display_3d:
        mlab.show()

    
def simulate(inner_teeth, outer_teeth, pencil_percent, offset_rad, display_2d=False, display_3d=False, save_to_obj=False, gear_name="Simulation"):
    points = []
    total_rads = 0
    pencil_radius = pencil_percent * inner_teeth
    r_diff = outer_teeth - inner_teeth

    lcm = np.lcm(inner_teeth, outer_teeth)
    rotations = lcm / inner_teeth

    while total_rads < rotations * 2 * math.pi:
        x = r_diff * math.cos(total_rads) + pencil_radius * math.cos(
            (r_diff / inner_teeth) * total_rads)
        y = r_diff * math.sin(total_rads) - pencil_radius * math.sin(
            (r_diff / inner_teeth) * total_rads)
        z = r_diff * math.cos(total_rads) - pencil_radius * math.cos(
            (r_diff / inner_teeth) * total_rads)
        points.append((x, y, z))
        total_rads += THETA_STEP

    line = geom.LineString(points).buffer(.01)
    line = affin.rotate(line, offset_rad, geom.Point(0,0), use_radians=True)

    if display_2d:
        show_2d_plot(line, outer_teeth, gear_name)
    if display_3d or save_to_obj:
        show_3d_plot(points, outer_teeth, gear_name, display_3d, save_to_obj)

    return line
