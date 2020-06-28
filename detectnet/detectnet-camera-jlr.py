#!/usr/bin/python
#
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import jetson.inference
import jetson.utils
import cv2 as cv
import argparse
import sys
import numpy as np
from datetime import datetime

import paho.mqtt.client as mqtt

client = mqtt.Client("face")
client.connect('mosquitto',port=1883)

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                           formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="none", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.4, help="minimum detection threshold to use") 
parser.add_argument("--camera", type=str, default="0", help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=1280, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")

try:
    opt = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

# load the object detection network
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

# create the camera and display
camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)
#display = jetson.utils.glDisplay()

# process frames until user exits
count = 0
start = datetime.now()

while True:
    # capture the image
    img, width, height = camera.CaptureRGBA(zeroCopy=1)

    # detect objects in the image (with overlay)
    detections = net.Detect(img, width, height, opt.overlay)
    
    # print the detections
    print("detected {:d} objects in image".format(len(detections)))

    for detection in detections:

        y_min = int(detection.Bottom)
        y_max = y_min - int(detection.Height)
        x_min = int(detection.Left)
        x_max = x_min + int(detection.Width)
        arr = jetson.utils.cudaToNumpy(img, width, height, 4)

        crop_arr = cv.cvtColor(arr[y_max:y_min,x_min:x_max,:-1], cv.COLOR_RGB2BGR)
        img = cv.resize(crop_arr,(96,96))/255.
        #cv.imwrite('/jetson_lip_reading/tom/{}.jpg'.format(count), img)
        # Encode as PNG
        rc, png = cv.imencode('.png', img)
        
        client.publish('facestream', payload=png.tobytes())
        count += 1
        if count == 90:
            print(f"Found 90 faces: {datetime.now()-start}")
            count = 0
            start = datetime.now()
            break
        break
            
    if cv.waitKey(10)==27:
        break


  