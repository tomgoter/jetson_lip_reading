import sys
import paho.mqtt.client as mqtt
import time
import os
import queue
import argparse

import numpy as np

from playsound import playsound

import io
from scipy.io import wavfile

# https://stackoverflow.com/questions/52369925/creating-wav-file-from-bytes
#import io
#import soundfile as sf

# https://stackoverflow.com/questions/43941716/how-to-play-mp3-from-bytes

#from pydub import AudioSegment
#from pydub.playback import play

#from pygame import mixer, time

##############
# Parameters #
##############

parser = argparse.ArgumentParser()

parser.add_argument("--sub_client_name", help="The name of the MQTT subscribing client", type=str, required=False, default="jetson-audio-receiver")
parser.add_argument("--sub_mqtt_host", help="The MQTT host for the subscribing client", type=str, required=True)
parser.add_argument("--sub_mqtt_port", help="The MQTT port for the subscribing client", type=int, required=False, default=1883)
parser.add_argument("--sub_qos", help="The MQTT quality of service for the subscribing client", type=int, required=False, default=2)
parser.add_argument("--sub_topic", help="The MQTT topic the subscribing client should subscribe to", type=str, required=False, default="jetson/audio")

args = parser.parse_args()

##############
# Core Logic #
##############

# make a queue of wav files to play
wav_bytes_queue = queue.Queue()
wav_files_queue = queue.Queue()

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

def on_subscribe(client, userdata, mid, granted_qos):
   print("subscribed")   

def convert_wav_bytes_to_wav_file(wav_bytes, wav_num):
   rate, data = wavfile.read(io.BytesIO(wav_bytes))
   outfile = save_wav(data, rate, wav_num)
   wav_files_queue.put(outfile, block=True)

wav_num = 0
def on_message(client, userdata, message):
   print("message topic=", message.topic)
   print("message qos=", message.qos)
   print("message retain flag=", message.retain)
   print("\n")

   # queue up message to be played
   #wav_bytes_queue.put(message.payload, block=True)
   global wav_num
   convert_wav_bytes_to_wav_file(message.payload, wav_num)
   wav_num += 1

   
# Set up client & callbacks
client = mqtt.Client(args.sub_client_name)
client.on_log = on_log
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(args.sub_mqtt_host, args.sub_mqtt_port)

# start client & subscribe client to topic
client.loop_start()
client.subscribe(args.sub_topic, args.sub_qos)

#mixer.pre_init(44100, -16, 2, 2048)
#mixer.init()

def save_wav(byte_data, rate, wav_num):
   outfile = '{}{}.wav'.format("./tmp/", wav_num)
   wavfile.write(outfile, rate, byte_data.astype(np.int16))
   return outfile

def process_wav_bytes(wav_bytes, wav_num):
   rate, data = wavfile.read(io.BytesIO(wav_bytes))
   
   # saving the wav file and playing -- works great, just theoretically slower
   outfile = save_wav(data, rate, wav_num)
   playsound(outfile)
      

   '''
   # pydub -- had issues with ffprobe errors
   song = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
   play(song)
   '''

   '''
   # pygame -- sounds like crap...
   sound = mixer.Sound(wav_bytes)
   audio = sound.play()
   while audio.get_busy():
      time.Clock().tick(10)
   '''

   '''
   # soundfile -- can't get import to work
   data, samplerate = sf.read(io.BytesIO(wav_bytes))
   '''


'''
# Wait for messages until disconnected by system interrupt
wav_num = 0
while True:
   if (wav_bytes_queue.qsize() > 0):
      # case: queuing wav bytes
      #process_wav_bytes(wav_bytes_queue.get(block=True), wav_num)
      wav_num += 1
'''


def process_wav_bytes():
   # Wait for messages until disconnected by system interrupt
   while True:
      try:
         if (wav_files_queue.qsize() > 0):
            # case: queuing file paths to saved wav files
            playsound(wav_files_queue.get(block=True))
      except KeyboardInterrupt:
         exit(0)
      '''
      except Exception as e:
         print(e)
         continue
      '''

# Run the process wav bytes function
process_wav_bytes()




