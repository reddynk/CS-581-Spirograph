import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox

import shapely.geometry as geom
import shapely.affinity as affin
from descartes import PolygonPatch

import math
import simulate
import gear
import pdf
import ast


s = open('pointcombos.txt', 'r').read()
pointcombos = ast.literal_eval(s)


inner_teeth = 96
outer_teeth = 144


points = 7

fig = plt.figure()
ax = fig.add_subplot(111)

axis_size = round(outer_teeth)
ax.axis((-axis_size, axis_size, -axis_size, axis_size))
ax.set_aspect(1)

#Slider
axcolor = 'lightgoldenrodyellow'
axpoint = plt.axes([0.20, 0.03, 0.65, 0.025], facecolor=axcolor)

spoint = Slider(axpoint, 'Point Position', 0.0, 0.95, valinit=0.0, valstep=0.01)

def update(val):
    pos = spoint.val
    line = simulate.simulate(inner_teeth, outer_teeth, pos, 0)
    
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

#Gear Combinations
rax = plt.axes([0.025, 0.4, 0.15, 0.3], facecolor=axcolor)

def setcombos():
    global points
    t = ()
    if points not in pointcombos.keys():
        raise "No combination of gears gives a figure with these number of points"
    else:
        ls = pointcombos[points]
        for i in ls:
            outer = i[0]
            inner = i[1]     
            if len(t) < 10:
                t = t + (str(outer) + '/' + str(inner), )
        return t
 
radio = RadioButtons(rax, setcombos(), active=0)

def changecombo(label):
    global outer_teeth
    global inner_teeth
    outer_teeth, inner_teeth = label.split("/")
    outer_teeth = int(outer_teeth)
    inner_teeth = int(inner_teeth)
    update(spoint.val)
    updateangle(sangle.val)

radio.on_clicked(changecombo)
    

#Number of Points
pointax = plt.axes([0.025, 0.8, 0.15, 0.10], facecolor=axcolor)
pointbox = TextBox(pointax, ' ', initial = "7")
pointax.text(0, 1, "Number of Points on Figure")

def changepoints(label):
    global points
    global rax
    global radio
    points = int(label)
    if points > 80:
        raise "choose a smaller point combination"
    else:
        rax.clear()
        radio = RadioButtons(rax, setcombos(), active=0)
        radio.on_clicked(changecombo)
        changecombo(radio.value_selected)
        #update(spoint.val)

pointbox.on_submit(changepoints)

#2D/3D Toggle
toggleax = plt.axes([0.025, 0.2, 0.05, 0.05], facecolor=axcolor)
togglebutton = Button(toggleax, ' ')
toggleax.text(0, 1, "View in 3D")

def switch(label):
    pos = spoint.val
    simulate.simulate(inner_teeth, outer_teeth, pos, 0, False, True, True)

togglebutton.on_clicked(switch)

#Create File
fileax = plt.axes([0.8, 0.6, 0.15, 0.15], facecolor=axcolor)
filebutton = Button(fileax, 'Generate Pdf')

def createfile(label):
    outer_gear, outer_gear_radius = gear.generate_outer_gear(outer_teeth)
    inner_gear, outer_radius, inner_radius = gear.generate_inner_gear(inner_teeth)
    inner_gear = gear.add_holes(inner_gear, inner_radius, [(spoint.val, sangle.val * math.pi / 180)])

    pdf.create("Inner + Outer Gears", outer_gear_radius, outer_gear, inner_gear, 0.5)

filebutton.on_clicked(createfile)
    
changepoints(points)
#changecombo(radio.value_selected)
plt.show()
