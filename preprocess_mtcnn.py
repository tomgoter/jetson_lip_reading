# Python Script for preprocessing a speaker's set of video data
# Runs on train, validation, and test sets
# Just for testing, leverage the data specified in Dataset/mini_sample
# Usage: python preprocess.py --speaker_root Dataset/mini_sample --speaker chem

import sys
from os import listdir, path
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import argparse, os, cv2, traceback, subprocess
from tqdm import tqdm
from glob import glob
from synthesizer import audio
from synthesizer.hparams import hparams as hp


###################
# Initializations #
###################

# python version checking
if sys.version_info[0] < 3 and sys.version_info[1] < 2:
	raise Exception("Must be using >= Python 3.2")

# Ensure face detection model has already been downloaded (repo uses s3fd, could also use the one from hw3/hw7)
if not path.isfile('face_detection/detection/sfd/s3fd.pth'):
	raise FileNotFoundError('Save the s3fd model to face_detection/sfd/s3fd.pth before running this script!')

# Parse out arguments for script
parser = argparse.ArgumentParser()
parser.add_argument('--ngpu', help='Number of GPUs across which to run in parallel', default=1, type=int)
parser.add_argument('--batch_size', help='Single GPU Face detection batch size', default=16, type=int)
parser.add_argument("--speaker_root", help="Root folder of Speaker", required=True)
parser.add_argument("--resize_factor", help="Resize the frames before face detection", default=1, type=int)
parser.add_argument("--speaker", help="Helps in preprocessing", required=True, choices=["chem", "chess", "hs", "dl", "eh"])
parser.add_argument("--minsize", help="Minimum size of face to look for. Higher means less processing.", required=True, default=140, type=int)
args = parser.parse_args()

##############
# Core Logic #
##############

# Function for cropping the video frame to the particular speaker (likely to improve resolution)
# Note that the chess speaker and the dl speaker both consistently appear in only a fraction of the youtube video,
# whereas the chem speaker moves around the entire frame (likely why there's no cropping for chem option)
def crop_frame(frame, args):
	if args.speaker == "chem" or args.speaker == "hs" or args.speaker == "tom":
		return frame
	elif args.speaker == "chess":
		return frame[270:460, 770:1130]
	elif args.speaker == "dl" or args.speaker == "eh":
		return  frame[int(frame.shape[0]*3/4):, int(frame.shape[1]*3/4): ]
	else:
		raise ValueError("Unknown speaker!")
		exit()

# Instantiate Tensor RT MT CNN Model
mtcnn = TrtMtcnn()

## Use the TRT MTCNN Model to detect at most one face per image
def loop_and_detect(mtcnn, frames, directory, minsize=140):
    """Continuously capture images from camera and do face detection."""

    tic = time.time()
    start = tic
    count = 0

    # List of Frames captured from video is sent in. Sequentially process this list.
    for f, file in enumerate(frames):
        img  = cv2.imread(file)
        dets, landmarks = mtcnn.detect(img, minsize=minsize)
        
        count += 1
        if len(dets) > 0:
            for bb, ll in zip(dets, landmarks):
                # Grab the bounding box
                x1, y1, x2, y2 = int(bb[0]), int(bb[1]), int(bb[2]), int(bb[3])

                # Crop the face
                crop_img = img[y1:y2, x1:x2]

                # Only grab one face per image
                break
            # Write the cropped face image to file
            cv2.imwrite(path.join(directory, '{}.jpg'.format(f)), crop_img)
            toc = time.time()
        # If it is the last file for the given video clip, print the average FPS
        if f == len(frames)-1:
            print(f'Found {f+1} faces in {toc-start} seconds - {(f+1)/(toc-start)} FPS')
            

# Preprocesses a video file specified by the file name vfile
# Preprocessing includes extracting the audio of the video to generate an audio file (audio.wav)
# and running facial detection on each frame and writing the cropped face to (<image_num.jpg)
# Final preprocessed output data is written to a "preprocessed" directory
def process_video_file(vfile, args, gpu_id):	
	# Create a directory for preprocessed data
	fulldir = vfile.replace('/intervals/', '/preprocessed/')
	fulldir = fulldir[:fulldir.rfind('.')] # ignore extension
	os.makedirs(fulldir, exist_ok=True)

	# Extract audio from video file to be used in audo preprocessing
	wavpath = path.join(fulldir, 'audio.wav')
	if args.speaker == "hs" or args.speaker == "eh":
		template = 'ffmpeg -hide_banner -loglevel panic -threads 1 -y -i {} -async 1 -ac 1 -vn -acodec pcm_s16le -ar 16000 {}'
		command = template.format(vfile, wavpath)
	else:
		template = 'ffmpeg -loglevel panic -y -i {} -ar {} -f wav {}'
		command = template.format(vfile, hp.sample_rate, wavpath)
	subprocess.call(command, shell=True)

	# For each frame in the video file, crop the frame to the particular speaker and resize the frames (prior knowledge)
	# Accumulate these cropped frames to be used later
	# Note that this is not a deep learning technique, this is likely just to help face detection later on
	video_stream = cv2.VideoCapture(vfile)
	frames = []
	while 1:
		still_reading, frame = video_stream.read()
		if not still_reading:
			video_stream.release()
			break
		# Crop and Resize only the Chess, DL and EH speakers
		frame = crop_frame(frame, args)
		frame = cv2.resize(frame, (frame.shape[1]//args.resize_factor, frame.shape[0]//args.resize_factor))
		frames.append(frame)

	# Process frames sequentially
    loop_and_detect(mtcnn, fulldir, args.minsize)
    
    

# Preprocess the audio file extracted in process_video_file
# Generates a single file containing the melspectrogram and linearspectrogram for the audio segment
def process_audio_file(vfile, args, gpu_id):
	# Create directory for preprocessed data (for data writes)
	fulldir = vfile.replace('/intervals/', '/preprocessed/')
	fulldir = fulldir[:fulldir.rfind('.')] # ignore extension
	os.makedirs(fulldir, exist_ok=True)

	# Load Audio File
	wavpath = path.join(fulldir, 'audio.wav')
	wav = audio.load_wav(wavpath, hp.sample_rate)

	# Save the mel spectrograpm & linear spectrogram of the audio file in `mels.npz` file
	spec = audio.melspectrogram(wav, hp)
	lspec = audio.linearspectrogram(wav, hp)
	specpath = path.join(fulldir, 'mels.npz')
	np.savez_compressed(specpath, spec=spec, lspec=lspec)

	
def mp_handler(job):
	vfile, args, gpu_id = job
	try:
		process_video_file(vfile, args, gpu_id)
		process_audio_file(vfile, args, gpu_id)
	except KeyboardInterrupt:
		exit(0)
	except:
		traceback.print_exc()
		
def main(args):
	print('Started processing for {} with {} GPUs'.format(args.speaker_root, args.ngpu))

	if args.speaker == 'tom':
        filelist = glob(path.join(args.speaker_root, 'intervals/*/*.mov'))
    else:
        filelist = glob(path.join(args.speaker_root, 'intervals/*/*.mp4'))

	jobs = [(vfile, args, i%args.ngpu) for i, vfile in enumerate(filelist)]
	p = ThreadPoolExecutor(args.ngpu)

	futures = [p.submit(mp_handler, j) for j in jobs]
	_ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]

if __name__ == '__main__':
	main(args)
