import socket

nb=2 # 0- HIT-"139.162.222.115", 1 - open HiveMQ - broker.hivemq.com
brokers=[str(socket.gethostbyname('vmm1.saaintertrade.com')), str(socket.gethostbyname('broker.hivemq.com')),str("3.68.38.195")]
ports=['80','1883','1883']
usernames = ['MATZI','',''] # should be modified for HIT
passwords = ['MATZI','',''] # should be modified for HIT
broker_ip=brokers[nb]
port=ports[nb]
username = usernames[nb]
password = passwords[nb]
conn_time = 0 # 0 stands for endless
mzs=['matzi/','','']
sub_topics =[mzs[nb]+'#','#',"#"]
pub_topics = [mzs[nb]+'test','test','test']

broker_ip=brokers[nb]
broker_port=ports[nb]
username = usernames[nb]
password = passwords[nb]
sub_topic = sub_topics[nb]
pub_topic = pub_topics[nb]
main_topic="store-room-0479/"
updateTime=6000 #in miliseconds
emergency_topic=main_topic + "emergency"
drainNonDhtBarrelsToo=False #set if you want to drain also the non dht barrels
