# Runs inference on a test set of data and generates a synthesized audio file, using preprocessed video frames of faces
# Saves the synthesized audio file, as well as the ground truth audio file
# Usage: python complete_test_generate.py -d Dataset/chem -r Dataset/chem/test_results --preset synthesizer/presets/chem.json --checkpoint <path_to_checkpoint>

import synthesizer
from synthesizer import inference as sif
import numpy as np
import sys, cv2, os, pickle, argparse, subprocess
from tqdm import tqdm
from shutil import copy
from glob import glob

###################
# Initializations #
###################

parser = argparse.ArgumentParser()
parser.add_argument('-d', "--data_root", help="Speaker folder path", required=True)
parser.add_argument('-r', "--results_root", help="Speaker folder path", required=True)
parser.add_argument('-s', "--subfolder", help="Data subfolder", required=True)
parser.add_argument('--checkpoint', help="Path to trained checkpoint", required=True)
parser.add_argument("--preset", help="Speaker-specific hyper-params", type=str, required=True)
args = parser.parse_args()

##############
# Core Logic #
##############

class Generator(object):
    def __init__(self):
        super(Generator, self).__init__()
        self.synthesizer = sif.Synthesizer(verbose=False)

    # Reads in a set of files (container "windows") as images and resize them as needed
    # Returns an np array of T RGD images that are each H x W in dimension (total of Time x Height x Width x 3 dimensions)
    def read_window(self, window_fnames):
        window = []
        for fname in window_fnames:
            img = cv2.imread(fname)
            if img is None:
                raise FileNotFoundError('Frames maybe missing in {}. Delete the video to stop this exception!'.format(sample['folder']))
            img = cv2.resize(img, (sif.hparams.img_size, sif.hparams.img_size))
            window.append(img)
        images = np.asarray(window) / 255. # Time x Height x Width x 3
        return images

    # Synthesizes the spectrograms for each sample of input videos
    # Using these spectrograms, synthesizes an audio wav file that is eventually saved to the specified output file
    def vc(self, sample, outfile):
        hp = sif.hparams
        images = sample['images']
        all_windows = []
        i = 0
        while i + hp.T <= len(images):
            all_windows.append(images[i : i + hp.T])
            i += hp.T - hp.overlap

        # Synthesize Spectrogram
        for window_idx, window_fnames in enumerate(all_windows):
            images = self.read_window(window_fnames)
            s = self.synthesizer.synthesize_spectrograms(images)[0]
            if window_idx == 0:
                mel = s
            else:
                mel = np.concatenate((mel, s[:, hp.mel_overlap:]), axis=1)
            
        # Synthesize Audio based on spectrogram
        wav = self.synthesizer.griffin_lim(mel)
        sif.audio.save_wav(wav, outfile, sr=hp.sample_rate)


# Gets a list of preprocessed cropped faces (one face corresponds to a single video frame)
def get_image_list(split, data_root):
    filelist = []
    with open(os.path.join(data_root, '{}.txt'.format(split))) as vidlist:
        for vid_id in vidlist:
            vid_id = vid_id.strip()
            filelist.extend(list(glob(os.path.join(data_root, args.subfolder, vid_id, '*/*.jpg'))))
    return filelist

# Gets a list of preprocessed cropped faces from the test videos
def get_testlist(data_root):
    test_images = get_image_list('test', data_root)
    print('{} hours is available for testing'.format(len(test_images) / (sif.hparams.fps * 3600.)))
    test_vids = {}
    for x in test_images:
        x = x[:x.rfind('/')]
        test_vids[x] = True
    return list(test_vids.keys())

def to_sec(idx):
    frame_id = idx + 1
    sec = frame_id / float(sif.hparams.fps)
    return sec

# Defines a generator fo contiguous windows of an original video
# These contiguous windows are max of length sif.hparams.T
def contiguous_window_generator(vidpath):
    print('Working on {}'.format(vidpath))
    # Get all the frames to consider
    frames = glob(os.path.join(vidpath, '*.jpg'))

    # If the numer of frames is less than the max length of a contiguous window, return early
    if len(frames) < sif.hparams.T: return

    ids = [int(os.path.splitext(os.path.basename(f))[0]) for f in frames]
    sortedids = sorted(ids) # image numbers corresponding to video frames from the original video (output of preprocess.py) 
    end_idx = 0
    start = sortedids[end_idx]

    # Generate segments of T frames of face images and yield them to the caller
    while end_idx < len(sortedids):
        while end_idx < len(sortedids):
            if end_idx == len(sortedids) - 1:
                if sortedids[end_idx] + 1 - start >= sif.hparams.T: 
                    yield (to_sec(start), to_sec(sortedids[end_idx]), 
                    [os.path.join(vidpath, '{}.jpg'.format(x)) for x in range(start, sortedids[end_idx] + 1)])
                return
            else:
                if sortedids[end_idx] + 1 - start == sif.hparams.T:
                    yield (to_sec(start), to_sec(sortedids[end_idx]), 
                        [os.path.join(vidpath, '{}.jpg'.format(x)) for x in range(start, sortedids[end_idx] + 1)])
                    break
                elif sortedids[end_idx] + 1 == sortedids[end_idx + 1]:
                    end_idx += 1
                else:
                    if sortedids[end_idx] + 1 - start >= sif.hparams.T: 
                        yield (to_sec(start), to_sec(sortedids[end_idx]), 
                        [os.path.join(vidpath, '{}.jpg'.format(x)) for x in range(start, sortedids[end_idx] + 1)])
                    break
        
        end_idx += 1
        start = sortedids[end_idx]

if __name__ == '__main__':
    # Do param-based initializations
    with open(args.preset) as f:
        sif.hparams.parse_json(f.read()) ## add speaker-specific parameters
    sif.hparams.set_hparam('eval_ckpt', args.checkpoint)

    # Prep directories for results (make sure directories are clean)
    if not os.path.isdir(args.results_root):
        os.mkdir(args.results_root)
    GTS_ROOT = os.path.join(args.results_root, 'gts/')
    WAVS_ROOT = os.path.join(args.results_root, 'wavs/')
    files_to_delete = []
    if not os.path.isdir(GTS_ROOT):
        os.mkdir(GTS_ROOT)
    else:
        files_to_delete = list(glob(GTS_ROOT + '*'))
    if not os.path.isdir(WAVS_ROOT):
        os.mkdir(WAVS_ROOT)
    else:
        files_to_delete.extend(list(glob(WAVS_ROOT + '*')))
    for f in files_to_delete: os.remove(f)

    # Get list of file names of preprocessed cropped faces of test set to evaluate (run inference)
    videos = get_testlist(args.data_root)
    print('Processing {} videos'.format(len(videos)))
    # Generate audio sample for the given video frames of cropped faces
    g = Generator()
    for vid in tqdm(videos): # Note tqdm generates progress bar
        vidpath = vid + '/'

        # for each set of start segment (ss), end segment (es) and corresponding images that fall between ss and es
        # take the sample of images and generate a wav file with the synthesized audio
        # Save the synthesized audio file and the ground truth audio file
        for ss, es, images in tqdm(contiguous_window_generator(vidpath)):
    
            sample = {}
            sample['images'] = images

            # Generate and save the synthesized audio file
            vidname = vid.split('/')[-2] + '_' + vid.split('/')[-1]
            outfile = '{}{}_{}:{}.wav'.format(WAVS_ROOT, vidname, ss, es)
            try:
                g.vc(sample, outfile)
            except KeyboardInterrupt:
                exit(0)
            except Exception as e:
                print(e)
                continue

            # Save the ground truth audio file
            template = 'ffmpeg -y -loglevel panic -ss {} -i {} -to {} -strict -2 {}'
            command = template.format(ss, vidpath + 'audio.wav', (es-ss), '{}{}_{}:{}.wav'.format(GTS_ROOT, vidname, ss, es))
            subprocess.call(command, shell=True)
