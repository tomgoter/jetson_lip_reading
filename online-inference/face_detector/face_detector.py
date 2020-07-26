# General Imports
import time
import sys
import os
from os import listdir, path

# Image Processing / Face Detection Imports
import numpy as np
import cv2
from mtcnn.mtcnn import TrtMtcnn

# MQTT imports
import paho.mqtt.client as mqtt
mqtt.Client.connected_flag = False


# Parameters
PUBLISHING_CLIENT_NAME = str(sys.argv[1])
PUBLISHING_MQTT_HOST = str(sys.argv[2])
PUBLISHING_MQTT_PORT = int(sys.argv[3])
PUBLISHING_QOS = int(sys.argv[4])
PUBLISH_TO_TOPIC = str(sys.argv[5])

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


# Define camera to use for capturing images to analyze (1 corresponds to USB camera)
cam = cv2.VideoCapture(1)

# start up face detector and publish message to broker when a face is detected
face_detector = TrtMtcnn()
frame_counter = -1
while(True):
   # capture frame 
   ret, frame = cam.read()

   # identity faces
   start = time.time()
   faces, landmarks = face_detector.detect(frame, minsize=min_size)
   duration = time.time() - start
   print("duration = " + str(duration * 1000) + " ms (" + str(1 / duration) + " fps)")
   frame_counter += 1
   #print("did a detection")

   # extract & publish faces
   for bb in faces:
      print("saw a face")
      x1, y1, x2, y2 = int(bb[0]), int(bb[1]), int(bb[2]), int(bb[3])
      face = frame[y1:y2, x1:x2]

      rc, png = cv2.imencode('.png', face)
      message = png.tobytes()
      client.publish(PUBLISH_TO_TOPIC, payload=message, qos=PUBLISHING_QOS)

      if (len(faces) > 1):
         break; 


# do clean up
cam.release()
client.loop_stop()
client.disconnect()
