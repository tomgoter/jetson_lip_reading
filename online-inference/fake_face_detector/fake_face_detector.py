# General Imports
import time
import sys
import os
from os import listdir, path, isfile

# Face Grabbing Dependencies
import cv2

# MQTT imports
import paho.mqtt.client as mqtt
mqtt.Client.connected_flag = False


# Parameters
PUBLISHING_CLIENT_NAME = str(sys.argv[1])
PUBLISHING_MQTT_HOST = str(sys.argv[2])
PUBLISHING_MQTT_PORT = int(sys.argv[3])
PUBLISHING_QOS = int(sys.argv[4])
PUBLISH_TO_TOPIC = str(sys.argv[5])

SOURCE_DIRECTORY = str(sys.argv[6])

# Params taken from preprocessing script
min_size = 100 # found decently matched results on S3FD model for chem guy

#def on_log(client, userdata, level, buf):
#   print(buf)

def on_connect(client, userdata, flags, rc):
   if (rc == 0):
      client.connected_flag=True # set flag
      print("connected OK")
   else:
      print("Bad connection retruned code = ", rc)
      client.loop_stop()

def on_disconnect(client, userdata, rc):
   print("client disconnected ok")

#def on_publish(client, userdata, mid):
#   print("in on_publish callback mid = ", mid)


# Set up publishing client & callbacks
client = mqtt.Client(PUBLISHING_CLIENT_NAME)
#client.on_log = on_log
client.on_connect = on_connect
client.on_disconnect = on_disconnect
#client.on_publish = on_publish
client.connect(PUBLISHING_MQTT_HOST, PUBLISHING_MQTT_PORT)

# wait for client to establish connection to broker
client.loop_start()
while not client.connected_flag:
   print("waiting to connect...")
   time.sleep(1)

# start up face grabber and publish message to broker when a face is detected
fnames = [f for f in listdir(SOURCE_DIRECTORY) if isfile(join(SOURCE_DIRECTORY, f))]
frame_counter = -1
for fname in fnames:
   # extract & publish faces
   face = cv2.imread(fname)
   rc, png = cv2.imencode('.png', face)
   message = png.tobytes()
   client.publish(PUBLISH_TO_TOPIC, payload=message, qos=PUBLISHING_QOS)
   frame_counter += 1

# do clean up
client.loop_stop()
client.disconnect()
