# General Imports
import time
import sys
import os
from os import listdir, path

# Face Grabbing Dependencies
import cv2
import numpy as np

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


# Iterate through all cut directories in numerical order
cutdirs_and_nums = [(path.join(SOURCE_DIRECTORY, d), int(d[4:])) for d in listdir(SOURCE_DIRECTORY)] 
cutdirs_and_nums.sort(key=lambda x: x[1])
for cutdir in cutdirs_and_nums:
   cutdir_full = print(path.join(SOURCE_DIRECTORY, cutdir))

   # Grab all image file names in numerical order
   fnames_and_nums = [(path.join(cutdir_full, f), int(f[0:-4])) for f in listdir(cutdir_full)] 
   fnames_and_nums.sort(key=lambda x: x[1])

   # start up face grabber and publish message to broker when a face is detected
   frame_counter = -1
   for (fname, num) in fnames_and_nums:
      # extract & publish faces
      face = cv2.imread(fname, cv2.IMREAD_COLOR)
      if np.shape(face) == ():
         print("continuing? fname = " + str(fname) + ", " + str(num))
         continue
      print("fname = " + str(fname) + ", " + str(num))
      rc, png = cv2.imencode('.png', face)
      message = png.tobytes()
      client.publish(PUBLISH_TO_TOPIC, payload=message, qos=PUBLISHING_QOS)
      frame_counter += 1

# do clean up
client.loop_stop()
client.disconnect()
