#
import sys, os, argparse
from glob import glob
import concurrent.futures
import numpy as np


def process_video(video):
    #
    print('Working on Video File: {}'.format(video))
    # Create a list of images to downsample
    cut_list = os.listdir(os.path.join(args.input_dir,video))
   
    for cut in cut_list:

        # Make output directory
        os.makedirs(os.path.join(args.output_dir,video,cut), exist_ok=True)

        # Extract the files
        file_list = os.listdir(os.path.join(args.input_dir, video, cut))

        # Grab the id numbers and convert to int
        file_ids = [int(x.split('.')[0]) for x in file_list if x[-3:] == 'jpg']

        # Sort the id numbers
        sorted_ids = sorted(file_ids)

        # Counter to remake sequences
        counter = 0

        print("Removing every {} image".format(stopper))
        for id in sorted_ids:
            if id != 0 and (id+1) % stopper == 0:
                counter  = int((id+1) / stopper)
                continue
            else:
                os.system('cp {0}/{1}/{2}/{3}.jpg {4}/{1}/{2}/{5}.jpg'.format(
                    args.input_dir, video, cut, id, args.output_dir, (id-counter)))
                #os.system(f'cp {args.input_dir}/{video}/{cut}/{id}.jpg {args.output_dir}/{video}/{cut}/{id-counter}.jpg')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', "--input_dir", help="Path to images to edit", required=True)
    parser.add_argument('-o', "--output_dir", help="Path to images to edit", required=True)
    parser.add_argument('-n', "--num_cpus",type=int, help="Number of CPUs to use", default=1)
    parser.add_argument('--fps', type=float, choices=[10, 15, 20], help="Desired Output FPS", required=True)
    args = parser.parse_args()

    # Original Videos recorded at 30 FPS
    BASE_FPS = 30

    # Identify how frequently to remove a frame
    stopper = np.round(1 / (1 - (args.fps / BASE_FPS)),0)
    print('Stopper is {}'.format(stopper))
    # Make Output Director
    os.makedirs(args.output_dir, exist_ok=True)

    #
    videos = os.listdir(args.input_dir)
    
    #
    print("Modifying the preprocessed images from the following videos: {}".format(videos))
    with concurrent.futures.ProcessPoolExecutor(args.num_cpus) as executor:
        result = executor.map(process_video, videos)


  
