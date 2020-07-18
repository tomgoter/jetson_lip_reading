#
import sys, os, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', "--input_dir", help="Path to images to edit", required=True)
parser.add_argument('-o', "--output_dir", help="Path to images to edit", required=True)
parser.add_argument('--fps', type=int, choices=[10, 15, 20], help="Desired Output FPS", required=True)
args = parser.parse_args()

# Original Videos recorded at 30 FPS
BASE_FPS = 30

# Create a list of images to downsample
file_list = os.listdir(args.input_dir)

# Grab the id numbers and convert to int
file_ids = [int(x.split('.')[0]) for x in file_list if x[-3:] == 'jpg']

# Sort the id numbers
sorted_ids = sorted(file_ids)

# Counter to remake sequences
counter = 0

# Identify how frequently to remove a frame
stopper = int(1 / (1 - (args.fps / BASE_FPS)))
print(f"Removing every {stopper} image")
for s, id in enumerate(sorted_ids):
    if id != 0 and id % stopper == 0:
        counter += 1
        continue
    else:
        os.system(f'cp {args.input_dir}/{id}.jpg {args.output_dir}/{id-counter}.jpg')

  
  