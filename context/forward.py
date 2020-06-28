import paho.mqtt.client as mqtt
from datetime import datetime


LOCAL_MQTT_HOST="mosquitto"
LOCAL_MQTT_PORT=1883
LOCAL_MQTT_TOPIC="facestream"
# Keep remote host stuff commented out in case we also want to forward to cloud storage
#REMOTE_HOST="52.117.100.124"
#REMOTE_MQTT_TOPIC = "cloud_topic"

# Counter for unique file name
counter = 0

# Connection callback
def on_connect_local(client, userdata, flags, rc):
        print("connected to local broker with rc: " + str(rc))
        client.subscribe(LOCAL_MQTT_TOPIC)

#def on_connect_remote(client, userdata, flags, rc):
#        print("connected to remote broker with rc: " + str(rc))
        
#def on_publish_remote(client, userdata, mid):
#    print("published message")

# Define what happens as messages are received
def on_message(client,userdata, msg):
  global counter
  try:
      print("message received - size:"+str(len(msg.payload)))	

      # Grab the payload which is the binary numpy image array
      msg = msg.payload

      # Write three images per input - currently set to upconvert to 30 fps assuming 10 fps input
      for i in range(3):
        # Passing the jetson lip reading dir as a volume when running this container
        with open(f"/jetson_lip_reading/tom/image_{counter*3 + i}.png", 'wb') as file_out:
            file_out.write(msg)
      counter += 1

      #remote_mqttclient.publish(LOCAL_MQTT_TOPIC, payload=msg, qos=0, retain=False)
      #remote_mqttclient.publish(LOCAL_MQTT_TOPIC, payload='test', qos=0, retain=False)
  except:
    print("Unexpected error:", sys.exc_info()[0])

local_mqttclient = mqtt.Client()
#remote_mqttclient = mqtt.Client("cloud_client")
local_mqttclient.on_connect = on_connect_local
local_mqttclient.connect(LOCAL_MQTT_HOST, LOCAL_MQTT_PORT, 60)
#remote_mqttclient.on_connect = on_connect_remote
#remote_mqttclient.connect(REMOTE_HOST, LOCAL_MQTT_PORT,60)
#remote_mqttclient.on_publish = on_publish_remote
local_mqttclient.on_message = on_message


# go into a loop
local_mqttclient.loop_forever()
