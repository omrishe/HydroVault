import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import time
import datetime
from init import *
import json
import re
from database import *

global CONNECTED,clientname,connectionInfo,barrelsAmt
#sets default values
connectionInfo={"ip":broker_ip,"port":port,"username":username,"password":password}
barrelsAmt=0
if len(sys.argv) > 1:  # Check if sys.argv[1] is provided
    try:  # Try parsing the JSON string
        connectionInfo = json.loads(sys.argv[1])  
    except json.JSONDecodeError:
        print("Error: sys.argv[1] is not valid JSON")
if len(sys.argv) > 2 :
    try:
            barrelsAmt=int(sys.argv[2])
    except:
        print("invalid input of number of barrels")
CONNECTED = False
r=random.randrange(1,100000)
clientname="IOT_client-Id-"+str(r)

class Mqtt_client():
    
    def __init__(self):
        # broker IP adress:
        self.broker=connectionInfo["ip"]
        self.topic=''
        self.port='' 
        self.clientname=''
        self.username=''
        self.password=''        
        self.subscribeTopic=''
        self.publishTopic=''
        self.publishMessage=''
        self.on_connected_to_form = ''
          
        
    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)
        print(self.broker)
        print(self.topic)
            
    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        if rc==0:
            print("connected OK")
            CONNECTED = True
            self.on_connected_to_form();            
        else:
            print("Bad connection Returned code=",rc)
            
    def on_disconnect(self, client, userdata, flags, rc=0):
        CONNECTED = False
        print("DisConnected result code "+str(rc))
            
    def on_message(self, client, userdata, msg):
        global barrelsAmt
        topic=msg.topic
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        print("relay message from:"+topic, m_decode)
        print("amount of barrels left: " + str(barrelsAmt))
        barrelsAmt-=1
        if(m_decode!="emergency"):
            extractedValArr = re.search(r"terminating Barrel: (\d+)", m_decode)
            barrel_id_value = extractedValArr.group(0)  # The value after "change fluid value of barrel id: "
        if(barrelsAmt<1):#true-means all barrels have emptied
            mainwin.connectionDock.statusLabel.setText("true")
            mainwin.connectionDock.statusLabel.setStyleSheet("background-color: Green")
            if(drainNonDhtBarrelsToo):
                drainAllBarrels()
            print("all barrels are emptied")
            time.sleep(10)
            QApplication.quit()
                

    def connect_to(self):
        # Init paho mqtt client class        
        self.client = mqtt.Client(self.clientname, clean_session=True) # create new client instance        
        self.client.on_connect=self.on_connect  #bind call back function
        self.client.on_disconnect=self.on_disconnect
        self.client.on_log=self.on_log
        self.client.on_message=self.on_message
        self.client.username_pw_set(self.username,self.password)        
        print("Connecting to broker ",self.broker)        
        self.client.connect(self.broker,self.port)     #connect to broker                  
    
    def start_listening(self):        
        self.client.loop_start()            
    
    def subscribe_to(self, topic):
        if CONNECTED:
            self.client.subscribe(topic)

    def publish_to(self, topic, message):
        if CONNECTED:
            self.client.publish(topic,message,qos=1)         
      
class EmergencyDrainRelay(QDockWidget):
    def __init__(self,mc):
        QDockWidget.__init__(self)
        self.mc = mc
        self.mc.on_connected_to_form=self.on_connected
        #declare elements
        self.statusLabel = QPushButton("false",self)
        self.statusLabel.setStyleSheet("background-color: Red")
        #connect directly to broker
        self.connect()
        self.eReconnect=QPushButton("Reconnect", self)
        self.eReconnect.clicked.connect(self.connect)
        #set and add elements to layout
        layout=QFormLayout()
        widget = QWidget(self)
        widget.setLayout(layout)
        layout.addRow("reconnect:",self.eReconnect)
        layout.addRow("finished emptying:",self.statusLabel)
        self.setWidget(widget)
        self.setWindowTitle("Emergency Drain Relay")
        
    def on_connected(self):
        #set the button color to green on connected
        self.eReconnect.setStyleSheet("background-color: green")
        self.mc.subscribe_to(emergency_topic)
                    
    def connect(self):
        #sets values of client
        self.mc.broker=connectionInfo["ip"]
        self.mc.port=int(connectionInfo["port"])
        self.mc.clientName=clientname
        self.mc.username=connectionInfo["username"]
        self.mc.password=connectionInfo["password"]       
        self.mc.connect_to()        
        self.mc.start_listening()


     
class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
                
        # Init of Mqtt_client class
        self.mc=Mqtt_client()
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(830, 780, 400, 150)
        self.setWindowTitle("emergency Relay")        

        # Init QDockWidget object        
        self.connectionDock = EmergencyDrainRelay(self.mc)        
       
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)        
        


app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
