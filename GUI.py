import os
if os.path.exists("storeroom.db"):
    os.remove("storeroom.db")

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
import subprocess
import json
import sqlite3
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from database import *
from datamanager import dataManagerMainWindow
import re


# Creating Client name - should be unique 
global clientname,processes,connectionInfo,dataManager
processes=[]
r=random.randrange(1,100000)
clientname="IOT_client-Id-"+str(r)
class Mqtt_client():
    
    def __init__(self):
        # broker IP adress:
        self.broker=''
        self.topic=''
        self.port='' 
        self.clientname=''
        self.username=''
        self.password=''        
        self.subscribeTopic=''
        self.publishTopic=''
        self.publishMessage=''
        self.on_connected_to_form = ''
        
    # Setters and getters
    def set_on_connected_to_form(self,on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form
    def get_broker(self):
        return self.broker
    def set_broker(self,value):
        self.broker= value         
    def get_port(self):
        return self.port
    def set_port(self,value):
        self.port= value     
    def get_clientName(self):
        return self.clientName
    def set_clientName(self,value):
        self.clientName= value        
    def get_username(self):
        return self.username
    def set_username(self,value):
        self.username= value     
    def get_password(self):
        return self.password
    def set_password(self,value):
        self.password= value         
    def get_subscribeTopic(self):
        return self.subscribeTopic
    def set_subscribeTopic(self,value):
        self.subscribeTopic= value        
    def get_publishTopic(self):
        return self.publishTopic
    def set_publishTopic(self,value):
        self.publishTopic= value         
    def get_publishMessage(self):
        return self.publishMessage
    def set_publishMessage(self,value):
        self.publishMessage= value 
        
        
    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)
            
    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("connected OK")
            self.on_connected_to_form()
            global dataManager
            dataManager=subprocess.Popen(["python", "datamanager.py"])
            
        else:
            print("Bad connection Returned code=",rc)
            
    def on_disconnect(self, client, userdata, flags, rc=0):
        print("DisConnected result code "+str(rc))
            
    def on_message(self, client, userdata, msg):
        topic=msg.topic
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        print("message from:"+topic, m_decode)
        mainwin.GetBarrelInfoDock.update_mess_win(m_decode)
        if(msg.topic==main_topic + "0"):
            extractedValArr = re.search(r"change fluid value of barrel id: (\d+) to: (\d+)", m_decode)
            barrel_id_value = extractedValArr.group(1)  # The value after "change fluid value of barrel id: "
            new_value = extractedValArr.group(2)
            changeFluidValue(barrel_id_value,new_value)

            

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
        print("subscribed to topic:" + topic)       
        self.client.subscribe(topic)
              
    def publish_to(self, topic, message):
        self.client.publish(topic,message,qos=1)        
      
class ConnectionDock(QDockWidget):
    def __init__(self,mc):
        QDockWidget.__init__(self)
        global clientname
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput=QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
        
        self.ePort=QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)
        
        self.eClientID=QLineEdit()
        
        self.eClientID.setText(clientname)
        
        self.eUserName=QLineEdit()
        self.eUserName.setText(username)
        
        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        
        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL=QCheckBox()
        
        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)
        
        self.eConnectbtn=QPushButton("Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: red")
        
        formLayot=QFormLayout()
        formLayot.addRow("Host",self.eHostInput )
        formLayot.addRow("Port",self.ePort )
        formLayot.addRow("Client ID", self.eClientID)
        formLayot.addRow("User Name",self.eUserName )
        formLayot.addRow("Password",self.ePassword )
        formLayot.addRow("Keep Alive",self.eKeepAlive )
        formLayot.addRow("SSL",self.eSSL )
        formLayot.addRow("Clean Session",self.eCleanSession )
        formLayot.addRow("",self.eConnectbtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Connect") 
        
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
                    
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())        
        self.mc.connect_to()        
        self.mc.start_listening()
        global connectionInfo
        connectionInfo=json.dumps({"ip":self.mc.broker,"port":self.mc.port,"username":self.mc.username,"password":self.mc.password})
        self.mc.subscribe_to(main_topic + "0")
            
class AddBarrel(QDockWidget):

    def __init__(self,mc):
        QDockWidget.__init__(self)
        
        self.mc = mc        
        #declare elements
        self.eBarrelID=QLineEdit()
        self.eBarrelID.setValidator(QIntValidator())
        self.eBarrelID.setText("1")
        self.eBarrelAmtFluid=QLineEdit()
        self.eBarrelAmtFluid.setText("0")
        self.eBarrelAmtFluid.setValidator(QIntValidator())
        self.eBarrelTypeFluid=QLineEdit()
        self.eBarrelTypeFluid.setText("enter type of fluid")
        self.eFollowGroupIDBtn = QPushButton("Keep getting updated(starts DHT)",self)      
        self.eAddBarrel = QPushButton("Add Barrel",self)
        self.eDescriptionBox=QLineEdit() 
        formLayot=QFormLayout()
        #set element to form layout        
        formLayot.addRow("BarrelID",self.eBarrelID)
        formLayot.addRow("AmtOfFluid",self.eBarrelAmtFluid)
        formLayot.addRow("TypeOfFluid",self.eBarrelTypeFluid)
        formLayot.addRow("short description",self.eDescriptionBox)
        formLayot.addRow("",self.eFollowGroupIDBtn)
        formLayot.addRow("",self.eAddBarrel)
        #declare event handlers
        self.eFollowGroupIDBtn.clicked.connect(lambda: self.on_Follow_Button_click(True))
        self.eAddBarrel.clicked.connect(lambda: self.on_Follow_Button_click(False))
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setWidget(widget) 
        self.setWindowTitle("Add Barrel")         
       
    def on_Follow_Button_click(self,IsFollowed):
        message="barrel ID: " + self.eBarrelID.text() + " Amount of fluids: " +  self.eBarrelAmtFluid.text() + " type of fluids: " +  self.eBarrelTypeFluid.text() + "comment: " + self.eDescriptionBox.text()
        barrelInfo=json.dumps({"id":self.eBarrelID.text(),"amt":self.eBarrelAmtFluid.text(),"type":self.eBarrelTypeFluid.text(),"comment":self.eDescriptionBox.text()})
        topic=main_topic + self.eBarrelID.text()
        if(not isIDExist(self.eBarrelID.text())):
            self.mc.publish_to(topic, message)
            global connectionInfo
            insertDb(self.eBarrelID.text(),self.eBarrelTypeFluid.text(),self.eBarrelAmtFluid.text(),self.eDescriptionBox.text())
            printDb()
            if(IsFollowed):
                self.eFollowGroupIDBtn.setStyleSheet("background-color: yellow")
                subProcess=subprocess.Popen(["python", "BarrelDHT.py",connectionInfo,barrelInfo])
                global processes
                processes.append(subProcess)
                self.eAddBarrel.setStyleSheet("")
            else:
                self.eAddBarrel.setStyleSheet("background-color: yellow")
        else:
            print("error id exists already")     
    
class GetBarrelInfo(QDockWidget):


    def __init__(self,mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        
        self.eSubscribeBarrelID=QLineEdit()
        self.eSubscribeBarrelID.setText("#") 
        #set validator
        regex = QRegExp(r"^(100|[1-9][0-9]?|#)$")
        validator = QRegExpValidator(regex, self.eSubscribeBarrelID)
        self.eSubscribeBarrelID.setValidator(validator)
        self.eRecMess=QTextEdit()

        self.eSubscribeBarrelIDBtn = QPushButton("getBarrelsInfo",self)
        self.eSubscribeBarrelIDBtn.clicked.connect(self.on_button_subscribe_click)

        formLayot=QFormLayout()       
        formLayot.addRow("BarrelsGroupID",self.eSubscribeBarrelID)
        #formLayot.addRow("QOS",self.eQOS)
        formLayot.addRow("BarrelsLog",self.eRecMess)
        formLayot.addRow("",self.eSubscribeBarrelIDBtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setWidget(widget)
        self.setWindowTitle("Barrels Data Monitor")
        
    def on_button_subscribe_click(self):
        print("showing data on barrels" + main_topic + self.eSubscribeBarrelID.text())
        self.mc.subscribe_to(main_topic + self.eSubscribeBarrelID.text())
        self.eSubscribeBarrelIDBtn.setStyleSheet("background-color: yellow")
        
    
    # create function that update text in received message window
    def update_mess_win(self,text):
        self.eRecMess.append(text)
        
class bigRedButton(QDockWidget):

    def __init__(self,mc):
        QDockWidget.__init__(self)
        self.mc = mc 
        self.eEmergencyDrainBtn = QPushButton("emergency drain(publisher button)",self)
        self.eEmergencyDrainBtn.clicked.connect(self.on_emergency_Btn_click)

        layout=QVBoxLayout()
        widget = QWidget(self)
        widget.setLayout(layout)
        
        layout.addWidget(self.eEmergencyDrainBtn)
        self.setWidget(widget)
        self.setWindowTitle("Emergency Drain")

    def on_emergency_Btn_click(self):
        global connectionInfo
        self.eEmergencyDrainBtn.setStyleSheet("background-color: Red")
        subprocess.Popen(["python", "emergencyDrainBtn.py",connectionInfo])
        subprocess.Popen(["python", "emergencyDrainRelay.py",connectionInfo,str(len(processes))])
        

class guiMainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        # Init of Mqtt_client class
        self.mc=Mqtt_client()
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)
        # set up main window
        self.setGeometry(30, 100, 800, 800)
        self.setWindowTitle('Monitor GUI')        

        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)        
        self.AddBarrelDock =   AddBarrel(self.mc)
        self.GetBarrelInfoDock = GetBarrelInfo(self.mc)
        self.bigRedButtonDock = bigRedButton(self.mc)
        
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.AddBarrelDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.GetBarrelInfoDock)
        self.splitDockWidget(self.AddBarrelDock, self.GetBarrelInfoDock, Qt.Horizontal)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bigRedButtonDock)

        self.addDockWidget(Qt.BottomDockWidgetArea, self.bigRedButtonDock)
        self.splitDockWidget(self.AddBarrelDock, self.bigRedButtonDock, Qt.Vertical)

app = QApplication(sys.argv)
mainwin = guiMainWindow()
mainwin.show()
app.exec_()

