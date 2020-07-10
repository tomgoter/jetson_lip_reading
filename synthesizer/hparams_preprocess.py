from glob import glob
import os, pickle

def get_image_list(split, data_root):
    filelist = []
    with open(os.path.join(data_root, '{}.txt'.format(split))) as vidlist:
        for vid_id in vidlist:
            vid_id = vid_id.strip()
            filelist.extend(list(glob(os.path.join(data_root, 'preprocessed', vid_id, '*/*.jpg'))))   
    return filelist

# Default hyperparameters
hparams = {
    # Comma-separated list of cleaners to run on text prior to training and eval. For non-English
    # text, you may want to use "basic_cleaners" or "transliteration_cleaners".
    'cleaners':"english_cleaners",
    
    # If you only have 1 GPU or want to use only one GPU, please set num_gpus:0 and specify the 
    # GPU idx on run. example:
    # expample 1 GPU of index 2 (train on "/gpu2" only): CUDA_VISIBLE_DEVICES:2 python train.py 
    # --model:"Tacotron" --hparams:"tacotron_gpu_start_idx:2"
    # If you want to train on multiple GPUs, simply specify the number of GPUs available, 
    # and the idx of the first GPU to use. example:
    # example 4 GPUs starting from index 0 (train on "/gpu0"->"/gpu3"): python train.py 
    # --model:"Tacotron" --hparams:"tacotron_num_gpus:4, tacotron_gpu_start_idx:0"
    # The hparams arguments can be directly modified on this hparams.py file instead of being 
    # specified on run if preferred!
    
    # If one wants to train both Tacotron and WaveNet in parallel (provided WaveNet will be 
    # trained on True mel spectrograms), one needs to specify different GPU idxes.
    # example Tacotron+WaveNet on a machine with 4 or plus GPUs. Two GPUs for each model: 
    # CUDA_VISIBLE_DEVICES:0,1 python train.py --model:"Tacotron" 
	# --hparams:"tacotron_gpu_start_idx:0, tacotron_num_gpus:2"
    # Cuda_VISIBLE_DEVICES:2,3 python train.py --model:"WaveNet" 
	# --hparams:"wavenet_gpu_start_idx:2; wavenet_num_gpus:2"
    
    # IMPORTANT NOTE: If using N GPUs, please multiply the tacotron_batch_size by N below in the 
    # hparams! (tacotron_batch_size : 32 * N)
    # Never use lower batch size than 32 on a single GPU!
    # Same applies for Wavenet: wavenet_batch_size : 8 * N (wavenet_batch_size can be smaller than
    #  8 if GPU is having OOM, minimum 2)
    # Please also apply the synthesis batch size modification likewise. (if N GPUs are used for 
    # synthesis, minimal batch size must be N, minimum of 1 sample per GPU)
    # We did not add an automatic multi-GPU batch size computation to avoid confusion in the 
    # user"s mind and to provide more control to the user for
    # resources related decisions.
    
    # Acknowledgement:
    #	Many thanks to @MlWoo for his awesome work on multi-GPU Tacotron which showed to work a 
	# little faster than the original
    #	pipeline for a single GPU as well. Great work!
    
    # Hardware setup: Default supposes user has only one GPU: "/gpu:0" (Tacotron only for now! 
    # WaveNet does not support multi GPU yet, WIP)
    # Synthesis also uses the following hardware parameters for multi-GPU parallel synthesis.
    'tacotron_gpu_start_idx':0,  # idx of the first GPU to be used for Tacotron training.
    'tacotron_num_gpus':1,  # Determines the number of gpus in use for Tacotron training.
    'split_on_cpu':True,
    # Determines whether to split data on CPU or on first GPU. This is automatically True when 
	# more than 1 GPU is used.
    ###########################################################################################################################################
    
    # Audio
    # Audio parameters are the most important parameters to tune when using this work on your 
    # personal data. Below are the beginner steps to adapt
    # this work to your personal data:
    #	1- Determine my data sample rate: First you need to determine your audio sample_rate (how 
	# many samples are in a second of audio). This can be done using sox: "sox --i <filename>"
    #		(For this small tuto, I will consider 24kHz (24000 Hz), and defaults are 22050Hz, 
	# so there are plenty of examples to refer to)
    #	2- set sample_rate parameter to your data correct sample rate
    #	3- Fix win_size and and hop_size accordingly: (Supposing you will follow our advice: 50ms 
	# window_size, and 12.5ms frame_shift(hop_size))
    #		a- win_size : 0.05 * sample_rate. In the tuto example, 0.05 * 24000 : 1200
    #		b- hop_size : 0.25 * win_size. Also equal to 0.0125 * sample_rate. In the tuto 
	# example, 0.25 * 1200 : 0.0125 * 24000 : 300 (Can set frame_shift_ms:12.5 instead)
    #	4- Fix n_fft, num_freq and upsample_scales parameters accordingly.
    #		a- n_fft can be either equal to win_size or the first power of 2 that comes after 
	# win_size. I usually recommend using the latter
    #			to be more consistent with signal processing friends. No big difference to be seen
	#  however. For the tuto example: n_fft : 2048 : 2**11
    #		b- num_freq : (n_fft / 2) + 1. For the tuto example: num_freq : 2048 / 2 + 1 : 1024 + 
	# 1 : 1025.
    #		c- For WaveNet, upsample_scales products must be equal to hop_size. For the tuto 
	# example: upsample_scales:[15, 20] where 15 * 20 : 300
    #			it is also possible to use upsample_scales:[3, 4, 5, 5] instead. One must only 
	# keep in mind that upsample_kernel_size[0] : 2*upsample_scales[0]
    #			so the training segments should be long enough (2.8~3x upsample_scales[0] * 
	# hop_size or longer) so that the first kernel size can see the middle 
    #			of the samples efficiently. The length of WaveNet training segments is under the 
	# parameter "max_time_steps".
    #	5- Finally comes the silence trimming. This very much data dependent, so I suggest trying 
	# preprocessing (or part of it, ctrl-C to stop), then use the
    #		.ipynb provided in the repo to listen to some inverted mel/linear spectrograms. That 
	# will first give you some idea about your above parameters, and
    #		it will also give you an idea about trimming. If silences persist, try reducing 
	# trim_top_db slowly. If samples are trimmed mid words, try increasing it.
    #	6- If audio quality is too metallic or fragmented (or if linear spectrogram plots are 
	# showing black silent regions on top), then restart from step 2.
    'num_mels':80,  # Number of mel-spectrogram channels and local conditioning dimensionality
    #  network
    'rescale':True,  # Whether to rescale audio prior to preprocessing
    'rescaling_max':0.9,  # Rescaling value
    # Whether to clip silence in Audio (at beginning and end of audio only, not the middle)
    # train samples of lengths between 3sec and 14sec are more than enough to make a model capable
    # of good parallelization.
    'clip_mels_length':True,
    # For cases of OOM (Not really recommended, only use if facing unsolvable OOM errors, 
	# also consider clipping your samples to smaller chunks)
    'max_mel_frames':900,
    # Only relevant when clip_mels_length : True, please only use after trying output_per_steps:3
	#  and still getting OOM errors.
    
    # Use LWS (https://github.com/Jonathan-LeRoux/lws) for STFT and phase reconstruction
    # It"s preferred to set True to use with https://github.com/r9y9/wavenet_vocoder
    # Does not work if n_ffit is not multiple of hop_size!!
    'use_lws':False,
    # Only used to set as True if using WaveNet, no difference in performance is observed in 
    # either cases.
    'silence_threshold':2,  # silence threshold used for sound trimming for wavenet preprocessing
    
    # Mel spectrogram  
    'n_fft':800,  # Extra window size is filled with 0 paddings to match this parameter
    'hop_size':200,  # For 16000Hz, 200 : 12.5 ms (0.0125 * sample_rate)
    'win_size':800,  # For 16000Hz, 800 : 50 ms (If None, win_size : n_fft) (0.05 * sample_rate)
    'sample_rate':16000,  # 16000Hz (corresponding to librispeech) (sox --i <filename>)
    
    'frame_shift_ms':None,  # Can replace hop_size parameter. (Recommended: 12.5)
    
    # M-AILABS (and other datasets) trim params (these parameters are usually correct for any 
	# data, but definitely must be tuned for specific speakers)
    'trim_fft_size':512,
    'trim_hop_size':128,
    'trim_top_db':23,
    
    # Mel and Linear spectrograms normalization/scaling and clipping
    'signal_normalization':True,
    # Whether to normalize mel spectrograms to some predefined range (following below parameters)
    'allow_clipping_in_normalization':True,  # Only relevant if mel_normalization : True
    'symmetric_mels':True,
    # Whether to scale the data to be symmetric around 0. (Also multiplies the output range by 2, 
    # faster and cleaner convergence)
    'max_abs_value':4.,
    # max absolute value of data. If symmetric, data will be [-max, max] else [0, max] (Must not 
    # be too big to avoid gradient explosion, 
    # not too small for fast convergence)
    'normalize_for_wavenet':True,
    # whether to rescale to [0, 1] for wavenet. (better audio quality)
    'clip_for_wavenet':True,
    # whether to clip [-max, max] before training/synthesizing with wavenet (better audio quality)
    
    # Contribution by @begeekmyfriend
    # Spectrogram Pre-Emphasis (Lfilter: Reduce spectrogram noise and helps model certitude 
	# levels. Also allows for better G&L phase reconstruction)
    'preemphasize':True,  # whether to apply filter
    'preemphasis':0.97,  # filter coefficient.
    
    # Limits
    'min_level_db':-100,
    'ref_level_db':20,
    'fmin':55,
    # Set this to 55 if your speaker is male! if female, 95 should help taking off noise. (To 
	# test depending on dataset. Pitch info: male~[65, 260], female~[100, 525])
    'fmax':7600,  # To be increased/reduced depending on data.
    
    # Griffin Lim
    'power':1.5,
    # Only used in G&L inversion, usually values between 1.2 and 1.5 are a good choice.
    'griffin_lim_iters':60,
    # Number of G&L iterations, typically 30 is enough but we use 60 to ensure convergence.
    ###########################################################################################################################################

}


def hparams_debug_string():
    values = hparams.values()
    hp = ["  %s: %s" % (name, values[name]) for name in sorted(values) if name != "sentences"]
    return "Hyperparameters:\n" + "\n".join(hp)
