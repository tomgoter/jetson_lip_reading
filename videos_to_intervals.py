# -*- coding: utf-8 -*-
"""
Pre-pre-processor for Jetson Lip Reading Project

This is a simple script that cuts arbitrary length videos into 30 seconds 
chunks using the ffmpeg utility.

"""
import os
from glob import glob
from tqdm import tqdm
from glob import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--video_root", help="Root folder of raw videos", required=True)
parser.add_argument("--interval_root", help="where to create the interval files", required=True)
parser.add_argument("--fps", help="optional parameter to allow you to change the fps of the output video")

args = parser.parse_args()

video_list = [vid for vid in os.listdir(args.video_root) if '.mov' == vid[-4:]]
print("Total Number of Videos to Process {}".format(len(video_list)))

# Template string to run ffmpeg over and over with
if args.fps:
  template = 'ffmpeg -i {}/{} -c copy -segment_time 30 fps=fps={} -f segment {}/{}/cut-%d.mov'
else:
  template = 'ffmpeg -i {}/{} -c copy -segment_time 30 -f segment {}/{}/cut-%d.mov'

# Loop over videos and chunk
for vid in tqdm(video_list):
  base_path = vid[:-4]
  if not os.path.isdir(os.path.join(args.interval_root, base_path)):  
    os.mkdir(os.path.join(args.interval_root, base_path))
    if args.fps:
      os.system(template.format(args.video_root, vid, args.fps, args.interval_root, base_path))
    else:
      os.system(template.format(args.video_root, vid, args.interval_root, base_path))
  else:
    continue
    
