#
import sys, os, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', "--input_dir", help="Path to images to edit", required=True)
parser.add_argument('-o', "--output_dir", help="Path to images to edit", required=True)
args = parser.parse_args()

# List of videos
videos = os.listdir(args.input_dir)

for video in videos:
    print('Working on Video File: {}'.format(video))
    # Create a list of segments to process
    cut_list = os.listdir(os.path.join(args.input_dir,video))

    # Copy over the mels and wav files
    for cut in cut_list:
        os.system('cp {0}/{1}/{2}/mels.npz {3}/{1}/{2}/mels.npz'.format(args.input_dir, video, cut, args.output_dir))
        os.system('cp {0}/{1}/{2}/audio.wav {3}/{1}/{2}/audio.wav'.format(args.input_dir, video, cut, args.output_dir))




  
