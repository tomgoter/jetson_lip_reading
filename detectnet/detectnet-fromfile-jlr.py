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
import os


# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                           formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--threshold", type=float, default=0.4, help="minimum detection threshold to use") 
parser.add_argument("--directory", type=str, help="path to look for images")

try:
    opt = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

# Make an Output Directory for the faces
output_path = os.path.join(opt.directory, 'face')
if not os.path.isdir(output_path):
		os.mkdir(output_path)
else:
    os.system(f'rm {output_path}/*png')

# load the object detection network
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

# Read the list of files from the input directory
filelist = [file for file in os.listdir(opt.directory) if file[-3:]=='jpg']

# Create counter
count = 0

# Loop over each file and perform the detection.
for file in filelist:
    # load an image (into shared CPU/GPU memory)
    img, width, height = jetson.utils.loadImageRGBA(f'{opt.directory}{file}')
        
    # detect objects in the image (with overlay)
    detections = net.Detect(img, width, height, "none")
    
    # print the detections
    print("detected {:d} objects in image".format(len(detections)))

    for detection in detections:
        if detection.ClassID == 0:
            y_min = int(detection.Bottom)
            y_max = y_min - int(detection.Height)
            x_min = int(detection.Left)
            x_max = x_min + int(detection.Width)
            arr = jetson.utils.cudaToNumpy(img, width, height, 4)

            crop_arr = cv.cvtColor(arr[y_max:y_min,x_min:x_max,:-1], cv.COLOR_RGB2BGR)
            img = cv.resize(crop_arr,(48,48))/255.
            cv.imwrite(f'{output_path}/image_{count}.png', img)
            count += 1
            break


  