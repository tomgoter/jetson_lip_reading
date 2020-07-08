import paho.mqtt.client as mqtt
import os
import sys

LOCAL_MQTT_HOST = 'mqtt_cloud'
LOCAL_MQTT_PORT = 1883
LOCAL_MQTT_TOPIC = 'hw3_topic'

counter = 0

def on_subscribe(client, userdata, mid, granted_qos):
  print("Subscribed")

def on_connect_local(client, userdata, flags, rc):
  client.subscribe(LOCAL_MQTT_TOPIC, qos=1)
  print("connected to local broker with rc: " + str(rc))
	
def on_log(client, userdata, level, buf):
  print("log: ", buf)

def on_message(client,userdata, msg):
  global counter  
  try:
    print("message received!")
    with open("/images/image"+str(counter)+".png", 'wb') as file_out:
      file_out.write(msg.payload)     
    counter += 1
  except:
    print("Unexpected error:", sys.exc_info()[0])
  
local_mqttclient = mqtt.Client("in_the_cloud")
local_mqttclient.on_connect = on_connect_local
local_mqttclient.connect(LOCAL_MQTT_HOST, LOCAL_MQTT_PORT, 60)
local_mqttclient.on_message = on_message
local_mqttclient.on_subscribe = on_subscribe
local_mqttclient.on_log = on_log
# go into a loop
local_mqttclient.loop_forever()

