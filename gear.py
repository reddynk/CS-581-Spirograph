import sys
import numpy
import argparse
import itertools
import math

from shapely.ops import cascaded_union
from shapely.geometry import Point, MultiPoint, Polygon, box, LineString
from shapely.affinity import rotate, scale, translate

from matplotlib import pyplot as plt

from descartes import PolygonPatch

import simulate

import pdf

# import backwards

# TODO: Make some class that takes a poly and a radius. Pass that to pdf.py

# These have all been factored out in file wide constants.
# TODO: Experiment with different settings.
# Tooth width
TOOTH_WIDTH = 10.
# Pressure angle in degrees
PRESSURE_ANGLE = 20.
# Number of frames used to build the involute
FRAME_COUNT = 16
# Backlash
BACKLASH = 0.2
# Radius of each pencil hole
HOLE_RADIUS = 5
# Percent of radius of outer gear that will be the thickness of the outer gear.
THICKNESS_RATIO = .15
# Minimum thickness of outer gear.
MIN_WIDTH = 35
# Visual buffer used for display
BUFFER_FACTOR = 1.1
# Scale factor used for lasercut pdfs
SCALE_FACTOR = .5


def rot_matrix(x):
    c, s = numpy.cos(x), numpy.sin(x)
    return numpy.array([[c, -s], [s, c]])


def rotation(X, angle, center=None):
    if center is None:
        return numpy.dot(X, rot_matrix(angle))
    else:
        return numpy.dot(X - center, rot_matrix(angle)) + center


def deg2rad(x):
    return (numpy.pi / 180) * x


# Given information about a gear, calculates some values necessary for setting
# up the teeth around the gear. Tooth_width is given as a argument, even though
# it is a file constant, because for outer gears it is actually a function of
# the gear radius.
def calculate_gear_setup(tooth_width, teeth_count):
    true_tooth_width = tooth_width - BACKLASH
    pitch_circumference = true_tooth_width * 2 * teeth_count
    pitch_radius = pitch_circumference / (2 * numpy.pi)
    addendum = true_tooth_width * (2 / numpy.pi)
    return true_tooth_width, pitch_radius, addendum


def create_mark(radius, addendum, tooth_width, teeth_count, is_inner_mark):
    mark = Point(0, 0)
    if is_inner_mark:
        mark = LineString([Point(0, radius),
                           Point(0, radius + addendum)]).buffer(
                               tooth_width / 5)
    else:
        mark = LineString([
            Point(0, radius + (.75 * addendum)),
            Point(0, radius + (1.75 * addendum))
        ]).buffer(tooth_width / 5)

    mark = rotate(
        mark, (numpy.pi) / teeth_count, Point(0., 0.), use_radians=True)
    return mark


# Generate a gear with the given number of teeth
def generate_inner_gear(teeth_count, add_inner_mark=True):
    true_tooth_width, pitch_radius, addendum = calculate_gear_setup(
        TOOTH_WIDTH, teeth_count)
    dedendum = 1.25 * addendum
    outer_radius = pitch_radius + addendum
    inner_radius = pitch_radius - dedendum

    rad_pressure_angle = deg2rad(PRESSURE_ANGLE)

    # Tooth profile
    profile = numpy.array([
      [-(.5 * true_tooth_width + addendum * numpy.tan(rad_pressure_angle)),  addendum],
      [-(.5 * true_tooth_width - dedendum * numpy.tan(rad_pressure_angle)), -dedendum],
      [ (.5 * true_tooth_width - dedendum * numpy.tan(rad_pressure_angle)), -dedendum],
      [ (.5 * true_tooth_width + addendum * numpy.tan(rad_pressure_angle)) , addendum]
    ]) # yapf: disable

    poly_list = []
    prev_X = None
    l = 2 * true_tooth_width / pitch_radius
    for theta in numpy.linspace(0, l, FRAME_COUNT):
        X = rotation(profile + numpy.array(
            (-theta * pitch_radius, pitch_radius)), theta)
        if prev_X is not None:
            poly_list.append(
                MultiPoint([x for x in X] + [x for x in prev_X]).convex_hull)
        prev_X = X

    # Generate a tooth profile
    tooth_poly = cascaded_union(poly_list)
    tooth_poly = tooth_poly.union(scale(tooth_poly, -1, 1, 1, Point(0., 0.)))

    # Generate the full gear
    gear_poly = Point(0., 0.).buffer(outer_radius)

    for i in range(0, teeth_count):
        gear_poly = rotate(
            gear_poly.difference(tooth_poly), (2 * numpy.pi) / teeth_count,
            Point(0., 0.),
            use_radians=True)

    if add_inner_mark:
        # Create the mark in the topmost tooth.
        gear_poly = gear_poly.difference(
            create_mark(inner_radius, addendum, true_tooth_width, teeth_count,
                        True))
    else:
        # Create the mark just beyond the topmost tooth.
        gear_poly = gear_poly.union(
            create_mark(outer_radius, addendum, true_tooth_width, teeth_count,
                        False))

    # Job done
    return gear_poly, outer_radius, inner_radius


# TODO: Take width of square as an argument.
# Generate a gear with the given number of teeth
def generate_outer_gear(teeth_count, side_length=None):
    cutout, outer_radius, inner_radius = generate_inner_gear(
        teeth_count, add_inner_mark=False)

    if not side_length:
        thickness = max(outer_radius * THICKNESS_RATIO, MIN_WIDTH)
        side_length = (outer_radius + thickness) * 2

    frame = box(-side_length / 2, -side_length / 2, side_length / 2,
                side_length / 2)
    poly = frame.difference(cutout)

    return poly, side_length / 2


# Add a number of pencil circles to the given (inner gear).
def add_holes(poly, inner_radius, hole_list):
    '''for x, y in hole_list:
        hole_circle = Point(
            (2 * x * inner_radius) - inner_radius,
            (2 * y * inner_radius) - inner_radius).buffer(HOLE_RADIUS)
        poly = poly.difference(hole_circle)'''

    for prop, theta in hole_list:
        r = prop * inner_radius
        hole_circle = Point(r * math.cos(theta),
                            r * math.sin(theta)).buffer(HOLE_RADIUS)
        poly = poly.difference(hole_circle)

    return poly


def add_gear_figure(poly, outer_radius, gear_name):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.add_patch(PolygonPatch(poly))

    # The outer_radius is the distance from the center to the farthest point
    # on a tooth. Therefore, make the size of the axis just a bit bigger.
    axis_size = round(outer_radius) * BUFFER_FACTOR
    ax.axis((-axis_size, axis_size, -axis_size, axis_size))
    ax.set_title(gear_name)
    ax.set_aspect(1)


def main():
    # Generate the shape
    inner_teeth = 42
    inner_poly, outer_radius_innergear, inner_radius = generate_inner_gear(
        inner_teeth)
    inner_poly = add_holes(inner_poly, inner_radius, [(0.5, 0),
                                                      (0.45, 5 * math.pi / 2)])
    # add_gear_figure(inner_poly, outer_radius_innergear, "Inner Gear")

    outer_teeth = 96
    outer_poly, outer_radius_outergear = generate_outer_gear(outer_teeth)
    # add_gear_figure(outer_poly, outer_radius_outergear, "Outer Gear")

    # plt.show()

    simulate.simulate(inner_teeth,outer_teeth, .5, 0, display_2d=True, display_3d=True)

    # backwards.process()

    # pdf.create("spirograph_set", outer_radius_outergear, outer_poly, inner_poly, SCALE_FACTOR)


if __name__ == '__main__':
    main()
