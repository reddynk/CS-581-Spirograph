import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox, Widget

import shapely.geometry as geom
import shapely.affinity as affin
from descartes import PolygonPatch

import math
import createdictionary
import simulate
import gear
import pdf

inner_teeth = 106
outer_teeth = 144
pointlist = []
text = "Added Points:"

fig = plt.figure()
ax = fig.add_subplot(111)
txt = fig.text(0, 0.15, text)

axis_size = round(outer_teeth)
ax.axis((-axis_size, axis_size, -axis_size, axis_size))
ax.set_aspect(1)

#Slider
axcolor = 'lightgoldenrodyellow'
axpoint = plt.axes([0.20, 0, 0.65, 0.05], facecolor=axcolor)

spoint = Slider(axpoint, 'Point Position', 0.0, 1.0, valinit=0.0, valstep=0.01)

def update(val):
    pos = spoint.val

    line = simulate.simulate(inner_teeth, outer_teeth, pos, 0)
    
    for p in ax.patches:
        p.remove()
    ax.add_patch(PolygonPatch(line))
   
spoint.on_changed(update)


#Outer Gear Size
outerax = plt.axes([0.025, 0.8, 0.15, 0.10], facecolor=axcolor)
outerbox = TextBox(outerax, ' ',initial = "144")
outerax.text(0, 1,'Outer Gear Teeth')

def changeoutersize(label):
    global outer_teeth
    global ax
    ax.clear()
    axis_size = round(outer_teeth)
    ax.axis((-axis_size, axis_size, -axis_size, axis_size))
    ax.set_aspect(1)
    outer_teeth = int(label)
    update(spoint.val)

outerbox.on_submit(changeoutersize)

#Inner Gear Size
innerax = plt.axes([0.025, 0.6, 0.15, 0.10], facecolor=axcolor)
innerbox = TextBox(innerax, ' ', initial = "106")
innerax.text(0, 1,'Inner Gear Teeth')

def changeinnersize(label):
    global inner_teeth
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
    text = text + '\n' + str((spoint.val, 0))
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
plt.show()

