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



def generate(teeth_count):
	true_tooth_width = TOOTH_WIDTH - BACKLASH
	pitch_circumference = true_tooth_width * 2 * teeth_count
	pitch_radius = pitch_circumference / (2 * numpy.pi)
	rad_pressure_angle = deg2rad(PRESSURE_ANGLE)
	addendum = true_tooth_width * (2 / numpy.pi)
	dedendum = addendum
	outer_radius = pitch_radius + addendum
	# Tooth profile
	profile = numpy.array([
  	[-(.5 * true_tooth_width + addendum * numpy.tan(rad_pressure_angle)),  addendum],
  	[-(.5 * true_tooth_width - dedendum * numpy.tan(rad_pressure_angle)), -dedendum],
  	[ (.5 * true_tooth_width - dedendum * numpy.tan(rad_pressure_angle)), -dedendum],
  	[ (.5 * true_tooth_width + addendum * numpy.tan(rad_pressure_angle)) , addendum]
	])

	outer_circle = Point(0., 0.).buffer(outer_radius)

	poly_list = []
	prev_X = None
	l = 2 * true_tooth_width / pitch_radius
	for theta in numpy.linspace(0, l, FRAME_COUNT):
		X = rotation(profile + numpy.array((-theta * pitch_radius, pitch_radius)), theta)
		if prev_X is not None:
			poly_list.append(MultiPoint([x for x in X] + [x for x in prev_X]).convex_hull)
		prev_X = X	

	def circle_sector(angle, r):
		box_a = rotate(box(0., -2 * r, 2 * r, 2 * r), -angle / 2, Point(0., 0.))
		box_b = rotate(box(-2 * r, -2 * r, 0, 2 * r),  angle / 2, Point(0., 0.))
		return Point(0., 0.).buffer(r).difference(box_a.union(box_b))

	# Generate a tooth profile
	tooth_poly = cascaded_union(poly_list)
	tooth_poly = tooth_poly.union(scale(tooth_poly, -1, 1, 1, Point(0., 0.)))

	# Generate the full gear
	gear_poly = Point(0., 0.).buffer(outer_radius)
	for i in range(0, teeth_count):
		gear_poly = rotate(gear_poly.difference(tooth_poly), (2 * numpy.pi) / teeth_count, Point(0., 0.), use_radians = True)
	
	# Job done
	return gear_poly, pitch_radius


def main():

	# Generate the shape
	poly, pitch_radius = generate(17)

	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.add_patch(PolygonPatch(poly))
	
	# The pitch_radius is the distance from the center to the farthest point
	# on a tooth. Therefore, make the size of the axis just a bit bigger.
	axis_size = round(pitch_radius) * 1.25
	ax.axis((-axis_size,axis_size,-axis_size,axis_size))
	print("HERE")
	ax.set_title('Inner Gear')
	ax.set_aspect(1)

	plt.show()


if __name__ == '__main__':
	main()
