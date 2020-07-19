import paho.mqtt.client as mqtt
import time
import sys

# Subscribing client params
SUBSCRIBING_CLIENT_NAME = str(sys.argv[1])
SUBSCRIBING_MQTT_HOST = str(sys.argv[2])
SUBSCRIBING_MQTT_PORT = int(sys.argv[3])
SUBSCRIBING_QOS = int(sys.argv[4])
SUBSCRIBE_TO_TOPIC = str(sys.argv[5])

'''
# Publishing client params
PUBLISHING_CLIENT_NAME = str(sys.argv[6])
PUBLISHING_MQTT_HOST = str(sys.argv[7])
PUBLISHING_MQTT_PORT = int(sys.argv[8])
PUBLISHING_QOS = int(sys.argv[9])
PUBLISH_TO_TOPIC = str(sys.argv[10])
'''

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
   
   '''
   # publish message further on
   print("publishing message to topic")
   global sender_client
   ret = sender_client.publish(PUBLISH_TO_TOPIC, payload=message.payload, qos=PUBLISHING_QOS, retain=False)
   print("publish returned = ", str(ret))
   print("\n")
   '''

# Set up receiver client & callbacks
receiver_client = mqtt.Client(SUBSCRIBING_CLIENT_NAME)
receiver_client.on_log = on_log
receiver_client.on_connect = on_connect
receiver_client.on_disconnect = on_disconnect
receiver_client.on_message = on_message
receiver_client.on_subscribe = on_subscribe
receiver_client.connect(SUBSCRIBING_MQTT_HOST, SUBSCRIBING_MQTT_PORT)


'''
# Set up sender client & callbacks
sender_client = mqtt.Client(PUBLISHING_CLIENT_NAME)
sender_client.on_log = on_log
sender_client.on_connect = on_connect
sender_client.on_disconnect = on_disconnect
sender_client.on_publish = on_publish
sender_client.connect(PUBLISHING_MQTT_HOST, PUBLISHING_MQTT_PORT)
'''


# start clients & subscribe receiver client to topic
receiver_client.loop_start()
sender_client.loop_start()
receiver_client.subscribe(SUBSCRIBE_TO_TOPIC, SUBSCRIBING_QOS)

# Wait for messages until disconnected by system interrupt
while True:
   time.sleep(1)
