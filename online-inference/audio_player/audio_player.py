import paho.mqtt.client as mqtt
import time
import sys
import os

import numpy as np

from playsound import playsound

import io
from scipy.io import wavfile

# https://stackoverflow.com/questions/52369925/creating-wav-file-from-bytes
import io
import soundfile as sf

# Subscribing client params
SUBSCRIBING_CLIENT_NAME = str(sys.argv[1])
SUBSCRIBING_MQTT_HOST = str(sys.argv[2])
SUBSCRIBING_MQTT_PORT = int(sys.argv[3])
SUBSCRIBING_QOS = int(sys.argv[4])
SUBSCRIBE_TO_TOPIC = str(sys.argv[5])

# make a queue of wav files to play
wav_queue = queue.Queue()

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

def on_message(client, userdata, message):
   print("message topic=", message.topic)
   print("message qos=", message.qos)
   print("message retain flag=", message.retain)
   print("\n")

   # queue up message to be played
   wav_queue.put(message.payload, block=True)

   
# Set up client & callbacks
client = mqtt.Client(SUBSCRIBING_CLIENT_NAME)
client.on_log = on_log
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(SUBSCRIBING_MQTT_HOST, SUBSCRIBING_MQTT_PORT)

# start client & subscribe client to topic
client.loop_start()
client.subscribe(SUBSCRIBE_TO_TOPIC, SUBSCRIBING_QOS)

# Wait for messages until disconnected by system interrupt
wav_num = 0
while True:
   if (wav_queue.qsize() > 0):
      wav_bytes = wav_queue.get(block=True)
      rate, data = wavfile.read(wav_bytes)

      outfile = '{}{}.wav'.format("./tmp/", wav_num)
      wavfile.write(outfile, rate, data.astype(np.int16))
      
      wav_num += 1
      #data, samplerate = sf.read(io.BytesIO(wav_bytes))
