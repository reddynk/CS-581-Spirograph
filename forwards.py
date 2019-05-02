import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox, Widget

import shapely.geometry as geom
import shapely.affinity as affin
from descartes import PolygonPatch

import math
import simulate
import gear
import pdf

inner_teeth = 100
outer_teeth = 150
pointlist = []
text = "Added Points: \n (Distance, Radians)"

fig = plt.figure()
ax = fig.add_subplot(111)
txt = fig.text(0, 0.15, text)

axis_size = round(outer_teeth)
ax.axis((-axis_size, axis_size, -axis_size, axis_size))
ax.set_aspect(1)


#Slider
axcolor = 'lightgoldenrodyellow'
axpoint = plt.axes([0.20, 0.03, 0.65, 0.025], facecolor=axcolor)

spoint = Slider(axpoint, 'Point Position', 0.0, 0.95, valinit=0.0, valstep=0.01)

def update(val):
    pos = spoint.val

    if lcm(outer_teeth, inner_teeth) / inner_teeth > 90:
        raise "try a different ratio of teeth sizes"
    else:
        line = simulate.simulate(inner_teeth, outer_teeth, pos, sangle.val)
    
        for p in ax.patches:
            p.remove()
        ax.add_patch(PolygonPatch(line))
   
spoint.on_changed(update)

#SliderAngle
axangle = plt.axes([0.20, 0, 0.65, 0.025], facecolor=axcolor)

sangle = Slider(axangle, 'Angle Position', 0.0, 360, valinit=0.0, valstep=1)

def updateangle(val):
    angle = sangle.val


    line = simulate.simulate(inner_teeth, outer_teeth, spoint.val, angle)
    
    for p in ax.patches:
        p.remove()
    ax.add_patch(PolygonPatch(line))
   
sangle.on_changed(updateangle)


def lcm(x, y):
    greater = x
    while(True):
        if((greater % x == 0) and (greater % y == 0)):
            lcm = greater
            break
        greater += 1
    return lcm

#Outer Gear Size
outerax = plt.axes([0.025, 0.8, 0.15, 0.10], facecolor=axcolor)
outerbox = TextBox(outerax, ' ',initial = "150")
outerax.text(0, 1,'Outer Gear Teeth')

def changeoutersize(label):
    global outer_teeth
    global inner_teeth
    global ax
    if int(label) < inner_teeth:
        raise "Inner gear must be smaller than outer gear"
    else:
        ax.clear()
        axis_size = round(outer_teeth)
        ax.axis((-axis_size, axis_size, -axis_size, axis_size))
        ax.set_aspect(1)
        outer_teeth = int(label)
        update(spoint.val)

outerbox.on_submit(changeoutersize)

#Inner Gear Size
innerax = plt.axes([0.025, 0.6, 0.15, 0.10], facecolor=axcolor)
innerbox = TextBox(innerax, ' ', initial = "100")
innerax.text(0, 1,'Inner Gear Teeth')

def changeinnersize(label):
    global outer_teeth
    global inner_teeth
    if outer_teeth < int(label):
        raise "Inner gear must be smaller than outer gear"
    else:
        inner_teeth = int(label)
        update(spoint.val)

innerbox.on_submit(changeinnersize)

#Add point to gear
addpointax = plt.axes([0.025, 0.5, 0.05, 0.05], facecolor=axcolor)
pointbutton = Button(addpointax, ' ')
addpointax.text(0, 1,'Add Point')


def addpoint(label):
    global pointlist
    global txt
    global text
    pointlist.append((spoint.val, 0))
    text = text + '\n' + str((round(spoint.val, 2), round(sangle.val * math.pi / 180, 2)))
    txt.remove()
    txt = fig.text(0, 0.15, text)

pointbutton.on_clicked(addpoint)


#Create file
fileax = plt.axes([0.8, 0.6, 0.15, 0.15], facecolor=axcolor)
filebutton = Button(fileax, 'Generate Pdf')

def createfile(label):
    outer_gear, outer_gear_radius = gear.generate_outer_gear(outer_teeth)
    inner_gear, outer_radius, inner_radius = gear.generate_inner_gear(inner_teeth)
    inner_gear = gear.add_holes(inner_gear, inner_radius, pointlist)
    pdf.create("Inner + Outer Gears", outer_gear_radius, outer_gear, inner_gear, 0.5)

filebutton.on_clicked(createfile)

update(spoint.val)
updateangle(sangle.val)
plt.show()

