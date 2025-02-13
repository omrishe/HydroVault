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


global topic, CONNECTED ,clientname,connectionInfo,barrelInfo
#set default data to global variables,they either get updated later or recieved since this script is opened through gui
CONNECTED = False
barrelInfo={"id":"99","amt":"0","type":"0","comment":"invalid barrel"}
connectionInfo={"ip":broker_ip,"port":port,"username":username,"password":password}
if len(sys.argv) > 1:  # Check if sys.argv[1] is provided
    try:  # Try parsing the JSON string
        connectionInfo = json.loads(sys.argv[1])
        print(sys.argv[1]) 
    except json.JSONDecodeError:
        print("Error: sys.argv[1] is not valid JSON")
if len(sys.argv) > 2:  # Check if sys.argv[1] is provided
    try:  # Try parsing the JSON string
        barrelInfo = json.loads(sys.argv[2])  
    except json.JSONDecodeError:
        print("Error: sys.argv[2] is not valid JSON")
r=random.randrange(1,100000)
clientname="IOT_client-Id-"+str(r)

class Mqtt_client():
    
    def __init__(self):
        global barrelInfo,connectionInfo
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

    def set_on_connected_to_form(self,on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form
        
        
    def on_log(self, client, userdata, level, buf):
        global clientname
        print("clientname is :" + clientname)
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
        topic=msg.topic
        global barrelInfo
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        print("message from:"+topic, m_decode)
        if(m_decode=="emergency"):
                print(emergency_topic,"terminating Barrel: " + barrelInfo["id"])
                self.publish_to(emergency_topic,"terminating Barrel: " + barrelInfo["id"])
                msg="change fluid value of barrel id: " + barrelInfo["id"] + " to: " + "0"
                status=self.publish_to(main_topic + "0",msg)
                time.sleep(5)
        
        

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
    
    def disconnect_from(self):
        self.client.disconnect()                   
    
    def start_listening(self):        
        self.client.loop_start()        
    
    def stop_listening(self):        
        self.client.loop_stop()    
    
    def subscribe_to(self, topic):
        if CONNECTED:
            self.client.subscribe(topic)        
        
              
    def publish_to(self, topic, message):
        if CONNECTED:
            self.client.publish(topic,message,qos=1)
            return True         
      
class BarrelDht(QDockWidget):
    def __init__(self,mc):
        QDockWidget.__init__(self)
        self.mc = mc
        self.on_button_connect_click()
        #declare event handlers 
        self.eincreaseFluidInput=QLineEdit()
        self.eincreaseFluidInput.setValidator(QIntValidator())
        self.eincreaseFluidInput.setText("0")
        self.eDecreaseFluidInput=QLineEdit()
        self.eDecreaseFluidInput.setText("0")
        self.eDecreaseFluidInput.setValidator(QIntValidator())
        self.eChangeFluidVabtn=QPushButton(barrelInfo["amt"],self)
        self.eChangeFluidVabtn.clicked.connect(self.on_fluid_change_val_Btn)
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eConnectbtn=QPushButton("Enable/Connect", self)
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        layout=QFormLayout()
        layout.addRow("increase fluid value",self.eincreaseFluidInput )
        layout.addRow("decrease fluid value",self.eDecreaseFluidInput )
        layout.addRow("ChangeFluidAmt",self.eChangeFluidVabtn)
        layout.addRow("reconnect",self.eConnectbtn)
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setWindowTitle("Connect")
        
    def on_connected(self):
        self.mc.subscribe_to(emergency_topic)
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_fluid_change_val_Btn(self):
        global barrelInfo
        barrelInfo["amt"]=str(int(barrelInfo["amt"]) + int(self.eincreaseFluidInput.text()) - int(self.eDecreaseFluidInput.text()))
        msg="change fluid value of barrel id: " + barrelInfo["id"] + " to: " + barrelInfo["amt"]
        self.eChangeFluidVabtn.setText(barrelInfo["amt"])
        self.mc.publish_to(main_topic + "0",msg)
                    
    def on_button_connect_click(self):
        global clientname,barrelInfo
        self.mc.broker=connectionInfo["ip"]
        self.mc.port=int(connectionInfo["port"])
        self.mc.clientname=clientname
        self.mc.username=connectionInfo["username"]
        self.mc.password=connectionInfo["password"]
        self.mc.publishTopic=main_topic + str(barrelInfo["id"])
        self.mc.connect_to()        
        self.mc.start_listening()
        msg="barrel ID: " + barrelInfo["id"] + " Amount of fluids: " +  barrelInfo["amt"] + " type of fluids: " +  barrelInfo["type"] + "comment: " + barrelInfo["comment"]
        self.SendBarrelInfoLoop(self.mc.publishTopic,msg)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.SendBarrelInfoLoop(self.mc.publishTopic))
        self.timer.start(updateTime)

    def SendBarrelInfoLoop(self,topic,msg="none"):
        if(msg=="none"):
            msg="barrel ID: " + barrelInfo["id"] + " Amount of fluids: " +  barrelInfo["amt"] + " type of fluids: " +  barrelInfo["type"] + " comment: " + barrelInfo["comment"]
        self.mc.publish_to(topic, msg)


     
class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
                
        # Init of Mqtt_client class
        self.mc=Mqtt_client()
        self.setUnifiedTitleAndToolBarOnMac(True)
        # set up main window
        self.setGeometry(830, 530, 300, 150)
        self.setWindowTitle('barrel ID:' + str(barrelInfo["id"]) + "type:" + str(barrelInfo["type"]))        
        # Init QDockWidget objects        
        self.connectionDock = BarrelDht(self.mc)        
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)        
        


app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
