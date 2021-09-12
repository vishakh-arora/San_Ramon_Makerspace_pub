#!/usr/bin/python
import sys
import Adafruit_DHT
import paho.mqtt.client as mqtt
import time
import ssl
import logging
from mail import mail

connected= False
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global connected
    print("Connected with result code "+str(rc))
    connected = True

def on_disconnect(client, userdata, flags, rc):
    print("Disconnected with result code "+str(rc))

logging.basicConfig()
client = mqtt.Client()
#allow time to connect to io.adafruit
time.sleep(5)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.enable_logger()
client.username_pw_set(username="dvhs_makerspace")
client.tls_set_context()
#client.tls_set("/etc/ssl/certs/ca-certificates.crt")
#, tls_version=ssl.PROTOCOL_TLSv1_2)
try:
    print("Connecting")
    client.connect("io.adafruit.com", port=8883)
except Exception as err:
    print("Could not connect" + str(err))
    exit(2)
print("Starting loop")
client.loop_start()

#while True:
#    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
#    temperature = (temperature*(9.0/5))+32
#    print("Sending temp: " + str(temperature))

# Code for sending text if temp/humidity too low
#    if temperature < 50:
#        mail("9259646667@txt.att.net", "Temperature is too low: "+str(temperature))
#        time.sleep(2)
#    if humidity < 50:
#        mail("9259646667@txt.att.net", "Humidity is too low: "+str(humidity))
#	time.sleep(2)
    if (connected):
        try:
            print("Publishing")
            client.publish( 'dvhs_makerspace/feeds/hydro-temp',  payload=str(temperature))
            time.sleep(120)
            client.publish( 'dvhs_makerspace/feeds/hydro-humidity', payload=str(humidity))
            time.sleep(120)
        except Exception as e:
            print("Error publishing:" + str(e))
    else:
        print("Not yet connected")

#    fout.write('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity)+"\n")
#client.loop_forever()

