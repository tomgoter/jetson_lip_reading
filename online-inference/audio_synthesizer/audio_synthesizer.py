# System-related & MQTT imports
import time
import sys, os, pickle, argparse, subprocess
from tqdm import tqdm
from profilehooks import timecall
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

# Subscribing client params
parser.add_argument("--sub_client_name", help="The name of the MQTT subscribing client", type=str, required=True)
parser.add_argument("--sub_mqtt_host", help="The MQTT host for the subscribing client", type=str, required=True)
parser.add_argument("--sub_mqtt_port", help="The MQTT port for the subscribing client", type=int, required=True)
parser.add_argument("--sub_qos", help="The MQTT quality of service for the subscribing client", type=int, required=True)
parser.add_argument("--sub_topic", help="The MQTT topic the subscribing client should subscribe to", type=str, required=True)

# Publishing client params
'''
parser.add_argument("--pub_client_name", help="The name of the MQTT publishing client", type=str, required=True)
parser.add_argument("--pub_mqtt_host", help="The MQTT host for the publishing client", type=str, required=True)
parser.add_argument("--pub_mqtt_port", help="The MQTT port for the publishing client", type=int, required=True)
parser.add_argument("--pub_qos", help="The MQTT quality of service for the publishing client", type=int, required=True)
parser.add_argument("--pub_topic", help="The MQTT topic the publishing client should publish to", type=str, required=True)
'''

args = parser.parse_args()


##############
# Core Logic #
##############

# Do param-based initializations
with open(args.preset) as f:
   sif.hparams.parse_json(f.read()) ## add speaker-specific parameters
sif.hparams.set_hparam('eval_ckpt', args.checkpoint)

# Set params for processing
num_frames = 30 # sif.hparams.T

# Define a frame queue 
face_queue = Queue()

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

def on_publish(client, userdata, mid):
   print("in on_publish callback mid = ", mid)

def on_subscribe(client, userdata, mid, granted_qos):
   print("subscribed")

def on_message(client, userdata, message):
   print("message received")
   print("message topic=", message.topic)
   print("message qos=", message.qos)
   print("message retain flag=", message.retain)
   print("\n")

   # Put frame to python queue to be processed when batches of num_frames are available
   face = cv2.imdecode(message.payload)
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

'''
# Set up sender client & callbacks
sender_client = mqtt.Client(args.pub_client_name)
sender_client.on_log = on_log
sender_client.on_connect = on_connect
sender_client.on_disconnect = on_disconnect
sender_client.on_publish = on_publish
sender_client.connect(args.pub_mqtt_host, args.pub_mqtt_port)
'''

# start clients & subscribe receiver client to topic
receiver_client.loop_start()
sender_client.loop_start()
receiver_client.subscribe(args.sub_topic, args.sub_qos)


class Generator(object):
   def __init__(self):
      super(Generator, self).__init__()
      self.synthesizer = sif.Synthesizer(verbose=False)

   def convert_to_wav_and_save(self, images, outfile):
      # Resize images
      images = [cv2.resize(img, (sif.hparams.img_size, sif.hparams.img_size)) for img in images]
      images = np.asarray(images) / 255.

      # Synthesize Spectrogram
      mel_spec = self.synthesizer.synthesize_spectrograms(images)[0]         
         
      # Synthesize Audio based on spectrogram
      wav = self.synthesizer.griffin_lim(mel_spec)

      # Save synthesized wav to outputfile location
      sif.audio.save_wav(wav, outfile, sr=hp.sample_rate)

# Initialize audio generator
wav_generator = Generator()

# Wait for messages until disconnected by system interrupt
audio_sample_num = 1
while True:
   # Check to see if queue has enough frames
   if (face_queue.qsize() >= num_frames):
      print("reached " + str(num_frames) + " frames")

      # Fetch num_frames faces to process from the queue
      faces_to_process = []
      while (len(faces_to_process) != num_frames):
         faces_to_process.append(face_queue.get(block=True))

      # Process frames and generate synthesized audio
      try:
         outfile = '{}{}.wav'.format(WAVS_ROOT, audio_sample_num)
         start = time.time()
         wav_generator.convert_to_wav_and_save(faces_to_process, outfile)
         print("Converted " + str(num_frames) + " frames to wav in " + str(outfile) +
            ", duration: "+ str((time.time() - start) * 1000) + " ms")
         audio_sample_num += 1
      except KeyboardInterrupt:
         exit(0)
      except Exception as e:
         print(e)
         continue


