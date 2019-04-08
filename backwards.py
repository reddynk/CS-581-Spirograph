import PyQt5

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import createdictionary


#QApplication, QLabel, QLineEdit, QWidget, QFormLayout, QValidator


def process():
    app = QApplication([])
    win = QWidget()
    win.setWindowTitle("Backwards Process")
    #self.setGeometry(self.left, self.top, self.width, self.height)
    getInteger(win)
    #getHeight(win)
    win.show()
    app.exec_()

def getInteger(self):
    i, okPressed = QInputDialog.getInt(self, "Input Number of Points","Points:", 1, 1, 999, 1)
    if okPressed:
        numPoints = i
        if i in createdictionary.point_combos:
            print(createdictionary.point_combos[i])
            getHeight(self)
        else:
            flo = QFormLayout()
            e = QPushButton()
            flo.addRow("No combination of outer and inner gears are found", e)
            self.setLayout(flo)
        

def getHeight(self):
    e1 = QSlider(Qt.Horizontal)
    e1.setMinimum(0)
    e1.setMaximum(100)
    e1.setValue(20)
    flo = QFormLayout()
    flo.addRow(e1)
    self.setLayout(flo)
    #e1.valueChanged.connect(valuechange)
    #height = valuechange
    


    
##    app = QApplication([])
##    win = QWidget()
##
##    e1 = QLineEdit()
##    e1.setValidator(QIntValidator())
##    e1.setMaxLength(3)
##    e1.textChanged(textchanged)
##
##    e2 = QPushButton()
##    e2.setText("Enter")
##
##    flo = QFormLayout()
##    flo.addRow("Input the number of Points", e1)
##    flo.addRow(e2)
##
##    win.setLayout(flo)
##    win.setWindowTitle("Backwards Process")
##    win.show()
##    app.exec_()
##
##def textchanged(text):
##    numPoints = text
    
process()
#print(numPoints)
