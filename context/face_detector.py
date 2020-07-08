import numpy as np
import cv2
import os
from datetime import datetime
import subprocess as sp
#import paho.mqtt.client as mqtt

#client = mqtt.Client("face")
#client.connect('mosquitto',port=1883)


# Using HAAR Cascade Classifier for Face Detection
xml_path = '/usr/share/opencv4/haarcascades/'

face_cascade = cv2.CascadeClassifier(xml_path + 'haarcascade_frontalface_default.xml')

# 1 should correspond to /dev/video1 , your USB camera. The 0 is reserved for the TX2 onboard camera

# Set up GStreamer Pipeline
#gst_str = (" v4l2src device=/dev/video1 ! "
#               "video/x-raw, width=(int)1280, height=(int)720, format=YUY2 ! ")              
#               "videoconvert ! video/x-raw, format=RGB ! videoconvert !appsink name=appsink")
gst_str = ('v4l2src device=/dev/video1 ! '
                   'video/x-raw, width=(int)1280, height=(int)720 ! '
                   'videoconvert ! appsink')

#cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

command = [ 'ffmpeg', '-f', 'video4linux2',
        '-i', '/dev/video1',
        '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
        '-vcodec', 'rawvideo',
        '-an','-sn',              # we want to disable audio processing (there is no audio)
        '-']
pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

cap = cv2.VideoCapture(pipe)
#if not cap.isOpened:
#    print('--(!)Error opening video capture')
#    exit(0)
# process frames until user exits
count = 0

start = datetime.now()


while(True):
    # Capture frame-by-frame
    #ret, frame = cap.read()
    frame = pipe.stdout.read(640*480*3)
    frame = np.fromstring(frame, dtype='uint8')
    frame = frame.reshape((480,640,3))
    #
    if frame is None:
        print('--(!) No captured frame -- Break!')
        break
    
    # Convert to greyscale
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Arguments are the image, scale factor, and the number of neighbors for each candidate
    #faces = face_cascade.detectMultiScale(frame, 1.3, 5)
    count += 1
    print('did a detection')
    if count ==100:
        print(f'Captured 100 faces in {datetime.now()-start}')
        break
    #for (x,y,w,h) in faces:
        # Grab the face and dump it to bytes
        # The face resides between the start x and y plus the width and height
     #   face = frame[y:y+h,x:x+w]
        #cv2.imshow('Capture - Face Detection', face)
    #    count += 1

     #   if count == 100:
       #     print(f"Found 90 faces: {datetime.now()-start}")
      #      break
        # Encode as PNG
        #rc, png = cv2.imencode('.png', face)
        #msg = png.tobytes()
        #client.publish('hw3_topic', payload=msg)
    if cv2.waitKey(10) == 27:
        break

