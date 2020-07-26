# System-related & MQTT imports
import time
import sys, os, pickle, argparse, subprocess
from tqdm import tqdm
from profilehooks import timecall
import queue
import paho.mqtt.client as mqtt

# Synthesizer imports
import synthesizer
from synthesizer import inference as sif
import numpy as np
import cv2
from shutil import copy
from glob import glob


##############
# Parameters #
##############

parser = argparse.ArgumentParser()

# Synthesizer params
parser.add_argument("-d", "--data_root", help="Speaker folder path", required=True)
parser.add_argument("-r", "--results_root", help="Speaker folder path", required=True)
parser.add_argument("--checkpoint", help="Path to trained checkpoint", required=True)
parser.add_argument("--preset", help="Speaker-specific hyper-params", type=str, required=True)
parser.add_argument("--wav_action", help="What to do with the generated wav files", type=str, required=True, choices=["save", "forward"])

# Subscribing client params
parser.add_argument("--sub_client_name", help="The name of the MQTT subscribing client", type=str, required=True)
parser.add_argument("--sub_mqtt_host", help="The MQTT host for the subscribing client", type=str, required=True)
parser.add_argument("--sub_mqtt_port", help="The MQTT port for the subscribing client", type=int, required=True)
parser.add_argument("--sub_qos", help="The MQTT quality of service for the subscribing client", type=int, required=True)
parser.add_argument("--sub_topic", help="The MQTT topic the subscribing client should subscribe to", type=str, required=True)

# Publishing client params
parser.add_argument("--pub_client_name", help="The name of the MQTT publishing client", type=str, required=True)
parser.add_argument("--pub_mqtt_host", help="The MQTT host for the publishing client", type=str, required=True)
parser.add_argument("--pub_mqtt_port", help="The MQTT port for the publishing client", type=int, required=True)
parser.add_argument("--pub_qos", help="The MQTT quality of service for the publishing client", type=int, required=True)
parser.add_argument("--pub_topic", help="The MQTT topic the publishing client should publish to", type=str, required=True)

args = parser.parse_args()


##############
# Core Logic #
##############

# Do param-based initializations
with open(args.preset) as f:
   sif.hparams.parse_json(f.read()) ## add speaker-specific parameters
sif.hparams.set_hparam('eval_ckpt', args.checkpoint)
WAVS_ROOT = os.path.join(args.results_root, 'wavs/')
if not os.path.isdir(WAVS_ROOT):
   os.mkdir(WAVS_ROOT)

# Set params for processing
num_frames = sif.hparams.T

# Define a frame queue 
face_queue = queue.Queue()


def on_log(client, userdata, level, buf):
   print(buf)

def on_connect(client, userdata, flags, rc):
   if (rc == 0):
      print("connected OK")
   else:
      print("Bad connection retruned code = ", rc)
      client.loop_stop()

def on_disconnect(client, userdata, rc):
   print("client disconnected ok")

#def on_publish(client, userdata, mid):
#   print("in on_publish callback mid = ", mid)

def on_subscribe(client, userdata, mid, granted_qos):
   print("subscribed")

def on_message(client, userdata, message):
   #print("message received")
   #print("message topic=", message.topic)
   #print("message qos=", message.qos)
   #print("message retain flag=", message.retain)
   #print("\n")

   # Put frame to python queue to be processed when batches of num_frames are available
   face = np.asarray(bytearray(message.payload), dtype="uint8")
   face = cv2.imdecode(face, cv2.IMREAD_COLOR)
   face_queue.put(face, block=True)
   
   '''
   # publish message further on
   print("publishing message to topic")
   global sender_client
   ret = sender_client.publish(args.pub_topic, payload=message.payload, qos=args.pub_qos, retain=False)
   print("publish returned = ", str(ret))
   print("\n")
   '''


# Set up receiver client & callbacks
receiver_client = mqtt.Client(args.sub_client_name)
receiver_client.on_log = on_log
receiver_client.on_connect = on_connect
receiver_client.on_disconnect = on_disconnect
receiver_client.on_message = on_message
receiver_client.on_subscribe = on_subscribe
receiver_client.connect(args.sub_mqtt_host, args.sub_mqtt_port)


# Set up sender client & callbacks
sender_client = mqtt.Client(args.pub_client_name)
#sender_client.on_log = on_log
sender_client.on_connect = on_connect
sender_client.on_disconnect = on_disconnect
#sender_client.on_publish = on_publish
sender_client.connect(args.pub_mqtt_host, args.pub_mqtt_port)


# start clients & subscribe receiver client to topic
receiver_client.loop_start()
sender_client.loop_start()
receiver_client.subscribe(args.sub_topic, args.sub_qos)

class Generator(object):
   def __init__(self):
      super(Generator, self).__init__()
      self.synthesizer = sif.Synthesizer(verbose=False)
      self.synthesizer.load()

      self.mel_batches_per_wav_file = 2
      self.mel_batch = None
      self.num_mels = 0

   def generate_wav(self):
      if (self.num_mels != self.mel_batches_per_wav_file):
         print("not generating wav file yet...")
         return None
      else:
         print("Generating wav file of mel spectrograms")
         wav = self.synthesizer.griffin_lim(self.mel_batch)
         wav *= 32767 / max(0.01, np.max(np.abs(wav)))

         self.num_mels = 0
         self.mel_batch = None
         return wav

   def generate_and_save_wav(self, root_dir, wav_num):
      wav = self.generate_wav()
      if (wav is None):
         return
      else:
         print("saving wav file")
         outfile = '{}{}.wav'.format(root_dir, wav_num)
         sif.audio.save_wav(wav, outfile, sr=sif.hparams.sample_rate)

   def generate_and_forward_wav(self, mqtt_client, args):
      wav = self.generate_wav()
      if (wav is None):
         return
      else:
         print("forwarding wav file via MQTT")
         message = wav.tobytes()
         mqtt_client.publish(args.pub_topic, payload=message, qos=args.pub_qos)


   def generate_mel_spec(self, images):
      # Resize images
      images = [cv2.resize(img, (sif.hparams.img_size, sif.hparams.img_size)) for img in images]
      images = np.asarray(images) / 255.

      # Synthesize Spectrogram
      mel_spec = self.synthesizer.synthesize_spectrograms(images)[0]         
         
      # Concatenate batches of mel spectrograms
      if self.num_mels == 0:
         self.mel_batch = mel_spec
         self.num_mels = 1
      else:
         self.mel_batch = np.concatenate((self.mel_batch, mel_spec[:, sif.hparams.mel_overlap:]), axis=1)
         self.num_mels += 1

# Initialize audio generator
generator = Generator()

# Wait for messages until disconnected by system interrupt
audio_sample_num = 1
while True:
   num_frames = sif.hparams.T
   print("queue size = " + str(face_queue.qsize()))

   # Check to see if queue has enough frames
   if (face_queue.qsize() >= num_frames):
      print("reached " + str(num_frames) + " frames")

      # Fetch num_frames faces to process from the queue
      faces_to_process = []
      while (len(faces_to_process) != num_frames):
         faces_to_process.append(face_queue.get(block=True))

      # Process frames and generate synthesized audio
      try:
         start = time.time()
         generator.generate_mel_spec(faces_to_process)
         print("Converted " + str(num_frames) + " frames to mel spectrogram, duration: "+ str((time.time() - start) * 1000) + " ms")

         if (args.wav_action == "save"):
            generator.generate_and_save_wav(WAVS_ROOT, audio_sample_num)
         elif (args.wav_action == "forward"):
            generator.generate_and_forward_wav(sender_client, args)

         audio_sample_num += 1
      except KeyboardInterrupt:
         exit(0)
'''
      except Exception as e:
         print(e)
         continue
'''


