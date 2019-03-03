import sys
import numpy
import argparse
import itertools

import backends.dxf
import backends.text

from shapely.ops import cascaded_union
from shapely.geometry import Point, MultiPoint, Polygon, box
from shapely.affinity import rotate, scale, translate

from matplotlib import pyplot as plt

from descartes import PolygonPatch

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
HOLE_RADIUS = 2.

def rot_matrix(x):
	c, s = numpy.cos(x), numpy.sin(x)
	return numpy.array([[c, -s], [s, c]])



def rotation(X, angle, center = None):
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

# Generate a gear with the given number of teeth
def generate_inner_gear(teeth_count):
	true_tooth_width, pitch_radius, addendum = calculate_gear_setup(TOOTH_WIDTH, teeth_count)
	dedendum = addendum
	outer_radius = pitch_radius + addendum

	rad_pressure_angle = deg2rad(PRESSURE_ANGLE)
	
	# Tooth profile
	profile = numpy.array([
  	[-(.5 * true_tooth_width + addendum * numpy.tan(rad_pressure_angle)),  addendum],
  	[-(.5 * true_tooth_width - dedendum * numpy.tan(rad_pressure_angle)), -dedendum],
  	[ (.5 * true_tooth_width - dedendum * numpy.tan(rad_pressure_angle)), -dedendum],
  	[ (.5 * true_tooth_width + addendum * numpy.tan(rad_pressure_angle)) , addendum]
	])

	poly_list = []
	prev_X = None
	l = 2 * true_tooth_width / pitch_radius
	for theta in numpy.linspace(0, l, FRAME_COUNT):
		X = rotation(profile + numpy.array((-theta * pitch_radius, pitch_radius)), theta)
		if prev_X is not None:
			poly_list.append(MultiPoint([x for x in X] + [x for x in prev_X]).convex_hull)
		prev_X = X	

	# Generate a tooth profile
	tooth_poly = cascaded_union(poly_list)
	tooth_poly = tooth_poly.union(scale(tooth_poly, -1, 1, 1, Point(0., 0.)))

	# Generate the full gear
	gear_poly = Point(0., 0.).buffer(outer_radius)
	for i in range(0, teeth_count):
		gear_poly = rotate(gear_poly.difference(tooth_poly), (2 * numpy.pi) / teeth_count, Point(0., 0.), use_radians = True)
	
	# Job done
	return gear_poly, outer_radius

# Generate a gear with the given number of teeth
def generate_outer_gear(teeth_count):
	true_tooth_width = TOOTH_WIDTH - BACKLASH
	pitch_circumference = true_tooth_width * 2 * teeth_count
	pitch_radius = pitch_circumference / (2 * numpy.pi)
	rad_pressure_angle = deg2rad(PRESSURE_ANGLE)
	addendum = true_tooth_width * (2 / numpy.pi)
	dedendum = addendum
	outer_radius = pitch_radius + addendum
	inner_radius = pitch_radius - dedendum
	
	# Tooth profile
	profile = numpy.array([
  	[-(.5 * true_tooth_width + addendum * numpy.tan(rad_pressure_angle)),  addendum],
  	[-(.5 * true_tooth_width - dedendum * numpy.tan(rad_pressure_angle)), -dedendum],
  	[ (.5 * true_tooth_width - dedendum * numpy.tan(rad_pressure_angle)), -dedendum],
  	[ (.5 * true_tooth_width + addendum * numpy.tan(rad_pressure_angle)) , addendum]
	])

	poly_list = []
	prev_X = None
	l = 2 * true_tooth_width / pitch_radius
	for theta in numpy.linspace(0, l, FRAME_COUNT):
		X = rotation(profile + numpy.array((-theta * pitch_radius, pitch_radius)), theta)
		if prev_X is not None:
			poly_list.append(MultiPoint([x for x in X] + [x for x in prev_X]).convex_hull)
		prev_X = X	

	# Generate a tooth profile
	tooth_poly = cascaded_union(poly_list)
	tooth_poly = tooth_poly.union(scale(tooth_poly, -1, 1, 1, Point(0., 0.)))
	tooth_poly = scale(tooth_poly,1,-1,1)
	tooth_poly = translate(tooth_poly,0,-addendum,0)

	# Generate the full gear
	gear_poly = Point(0., 0.).buffer(outer_radius+10)
	for i in range(0, teeth_count):
		gear_poly = rotate(gear_poly.difference(tooth_poly), (2 * numpy.pi) / teeth_count, Point(0., 0.), use_radians = True)

	# Now remove the inner portion where the concentric gear fits
	gear_poly = gear_poly.difference(Point(0., 0.).buffer(inner_radius))

	# Job done
	return tooth_poly, gear_poly

# Add a number of pencil circles to the given (inner gear).
def add_holes(poly, inner_radius, hole_list):
	for x,y in hole_list:
		hole_circle = Point((2*x*inner_radius)-inner_radius, (2*y*inner_radius)-inner_radius).buffer(HOLE_RADIUS)
		poly = poly.difference(hole_circle)
	return poly


def add_gear_figure(poly, outer_radius, gear_name):
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.add_patch(PolygonPatch(poly))
	
	# The outer_radius is the distance from the center to the farthest point
	# on a tooth. Therefore, make the size of the axis just a bit bigger.
	axis_size = round(outer_radius) * 1.1
	ax.axis((-axis_size,axis_size,-axis_size,axis_size))
	print("HERE")
	ax.set_title(gear_name)
	ax.set_aspect(1)


def main():

	# Generate the shape
	inner_poly, outer_radius = generate_inner_gear(17)
	add_gear_figure(inner_poly,outer_radius,"Inner Gear")
	# poly = add_holes(poly,inner_radius,[(0.5,0.5),(0.5,0.8),(0.4,0.3)])

	tooth_poly, gear_poly = generate_outer_gear(17)


	# fig = plt.figure()
	# ax = fig.add_subplot(131)
	# axis_size = round(pitch_radius) * 1.25
	# ax.axis((-axis_size,axis_size,-axis_size,axis_size))
	# ax.set_aspect(1)
	# ax.add_patch(PolygonPatch(inner_poly))

	# ax = fig.add_subplot(132)
	# axis_size = round(pitch_radius) * 1.25
	# ax.axis((-axis_size,axis_size,-axis_size,axis_size))
	# ax.set_aspect(1)
	# ax.add_patch(PolygonPatch(tooth_poly))
	
	# # TODO: The reason the outer gear teeth are all messed up is because the 
	# # space between the tooth polys are insufficient. When we point outwards,
	# # this is handled by the different of the circle's radius at the inside
	# # point (where the gear tooth meets the circle) and the outside point 
	# # (where the tooth meets open space). Therefore, we must give each tooth
	# # a buffer some fraction of the difference of these two circumferences.
	# ax = fig.add_subplot(133)
	# axis_size = round(pitch_radius) * 1.25
	# ax.axis((-axis_size,axis_size,-axis_size,axis_size))
	# ax.set_aspect(1)
	# ax.add_patch(PolygonPatch(gear_poly))

	# The pitch_radius is the distance from the center to the farthest point
	# on a tooth. Therefore, make the size of the axis just a bit bigger.
	print("HERE")
	# ax.set_title(gear_name)

	# add_gear_figure(poly,pitch_radius,"Outer Gear")	

	plt.show()


if __name__ == '__main__':
	main()
