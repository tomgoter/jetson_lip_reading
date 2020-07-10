# Python Script for preprocessing a speaker's set of video data
# Runs on train, validation, and test sets
# Just for testing, leverage the data specified in Dataset/mini_sample
# Usage: python preprocess.py --speaker_root Dataset/mini_sample --speaker chem

import sys
from os import listdir, path
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import argparse, os, cv2, traceback, subprocess
from tqdm import tqdm
from glob import glob
from synthesizer import audio_preprocess
from synthesizer.hparams_preprocess import hparams as hp
from mtcnn import MTCNN
import time


###################
# Initializations #
###################

# python version checking
if sys.version_info[0] < 3 and sys.version_info[1] < 2:
    raise Exception("Must be using >= Python 3.2")

# Parse out arguments for script
parser = argparse.ArgumentParser()
parser.add_argument('--ngpu', help='Number of GPUs across which to run in parallel', default=1, type=int)
parser.add_argument('--batch_size', help='Single GPU Face detection batch size', default=16, type=int)
parser.add_argument("--speaker_root", help="Root folder of Speaker", required=True)
parser.add_argument("--resize_factor", help="Resize the frames before face detection", default=1, type=int)
parser.add_argument("--speaker", help="Helps in preprocessing", required=True, choices=["chem", "chess", "hs", "dl", "eh"])
parser.add_argument("--minsize", help="Minimum size of face to look for. Higher means less processing.",  default=140, type=int)
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

## Use the TRT MTCNN Model to detect at most one face per image
def loop_and_detect(mtcnn, frames, directory):
    """Continuously capture images from camera and do face detection."""

    tic = time.time()
    start = tic
    count = 0

    # List of Frames captured from video is sent in. Sequentially process this list.
    for f, frame in enumerate(frames):

        result = mtcnn.detect_faces(frame)

        # Did we detect anything?
        if len(result) > 0:
            # Result is an array with alx0:x0+width the bounding boxes detected. We know that for 'ivan.jpg' there is only one.
            bounding_box = result[0]['box']

            # Extract the bounding box coordinates
            x0, y0, width, height = int(bounding_box[0]), int(bounding_box[1]), \
                                 int(bounding_box[2]), int(bounding_box[3])
            # Crop the face
            crop_img = frame[y0:y0+height, x0:x0+width]

            # Write the cropped face image to file
            cv2.imwrite(path.join(directory, '{}.jpg'.format(f)), crop_img)
            toc = time.time()
    # print the average FPS after processing all frames
    print(f'Processed {len(frames)} faces in {toc-start} seconds - {len(frames)/(toc-start)} FPS')


# Preprocesses a video file specified by the file name vfile
# Preprocessing includes extracting the audio of the video to generate an audio file (audio.wav)
# and running facial detection on each frame and writing the cropped face to (<image_num.jpg)
# Final preprocessed output data is written to a "preprocessed" directory
def process_video_file(vfile, args, mtcnn, gpu_id):
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
        command = template.format(vfile, hp['sample_rate'], wavpath)
    subprocess.call(command, shell=True)

    # For each frame in the video file, crop the frame to the particular speaker and resize the frames (prior knowledge)
    # Accumulate these cropped frames to be used later
    # Note that this is not a deep learning technique, this is likely just to help face detection later on
    print(f'Processing file: {vfile}')
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
    loop_and_detect(mtcnn, frames, fulldir)



# Preprocess the audio file extracted in process_video_file
# Generates a single file containing the melspectrogram and linearspectrogram for the audio segment
def process_audio_file(vfile, args, gpu_id):
    # Create directory for preprocessed data (for data writes)
    fulldir = vfile.replace('/intervals/', '/preprocessed/')
    fulldir = fulldir[:fulldir.rfind('.')] # ignore extension
    os.makedirs(fulldir, exist_ok=True)

    # Load Audio File
    wavpath = path.join(fulldir, 'audio.wav')
    wav = audio_preprocess.load_wav(wavpath, hp['sample_rate'])

    # Save the mel spectrograpm & linear spectrogram of the audio file in `mels.npz` file
    spec = audio_preprocess.melspectrogram(wav, hp)
    lspec = audio_preprocess.linearspectrogram(wav, hp)
    specpath = path.join(fulldir, 'mels.npz')
    np.savez_compressed(specpath, spec=spec, lspec=lspec)


def mp_handler(job):
    vfile, args, mtcnn, gpu_id = job
    try:
        process_video_file(vfile, args, mtcnn, gpu_id)
        process_audio_file(vfile, args, gpu_id)
    except KeyboardInterrupt:
        exit(0)
    except:
        traceback.print_exc()

def main(args):
    print('Started processing for {} with {} GPUs'.format(args.speaker_root, args.ngpu))

    # Instantiate Tensor RT MT CNN Model
    mtcnn = MTCNN(min_face_size=args.minsize)
    if args.speaker == 'tom':
        filelist = glob(path.join(args.speaker_root, 'intervals/*/*.mov'))
    else:
        filelist = glob(path.join(args.speaker_root, 'intervals/*/*.mp4'))

    jobs = [(vfile, args, mtcnn, i%args.ngpu) for i, vfile in enumerate(filelist)]
    p = ThreadPoolExecutor(args.ngpu)

    futures = [p.submit(mp_handler, j) for j in jobs]
    _ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]

if __name__ == '__main__':
    main(args)
