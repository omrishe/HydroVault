import os
import sys
import PyQt5
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json
import sqlite3
import csv
from database import *

class dataManagerMainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)  
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set main window dimension
        self.setGeometry(830, 100, 500, 400)
        self.setWindowTitle('dataManager-DB')        

        # Initialize text element and add it to the layout
        self.eRecMess = QTextEdit(self)
        formLayout = QFormLayout()
        formLayout.addRow("BarrelsInfo", self.eRecMess)

        # Create central widget and set layout
        centralWidget = QWidget(self)
        centralWidget.setLayout(formLayout)
        # Set central widget for the main window
        self.setCentralWidget(centralWidget)
        #set timer to update gui for updates
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.dataMng_add_msg)
        self.timer.start(30)
        
    def dataMng_add_msg(self):
            data=load_data()
            self.eRecMess.setText(data)
            


if __name__ == "__main__":    
    app = QApplication(sys.argv)
    mainwin = dataManagerMainWindow()
    mainwin.show()
    app.exec_()
