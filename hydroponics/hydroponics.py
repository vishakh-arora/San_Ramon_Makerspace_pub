#!/usr/bin/python
import sys
import Adafruit_DHT
import paho.mqtt.client as mqtt
import time
import ssl
import logging
#from common import mail
import RPi.GPIO as GPIO
import time


DELAY_BETWEEN_PUBLISH = 120
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER_PIN = 18
GPIO_ECHO_PIN = 24

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_PIN, GPIO.OUT)
GPIO.setup(GPIO_ECHO_PIN, GPIO.IN)

connected= False

def distance():

    GPIO.output(GPIO_TRIGGER_PIN, GPIO.LOW)
    # Wait for sensor to settle
    time.sleep(2)

    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER_PIN, GPIO.HIGH)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER_PIN, GPIO.LOW)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO_PIN) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO_PIN) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

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
client.username_pw_set(username="dvhs_makerspace", password="6661ef63f9954314b99249cebf9d1d4f")
client.tls_set_context()
#client.tls_set("/etc/ssl/certs/ca-certificates.crt")
#, tls_version=ssl.PROTOCOL_TLSv1_2)
try:
    print("Connecting")
    client.connect("io.adafruit.com", port=8883)
except Exception as err:
    print("Could not connect" + str(err))
    exit(2)
#print("Starting loop")
client.loop_start()

while True:
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    if temperature != None:
    	temperature = (temperature*(9.0/5))+32
    dist = distance()
#    print("Sending temp: " + str(temperature)+"  humidity: "+str(humidity)+"  distance: "+str(dist))
    time.sleep(2)

# Code for sending text if temp/humidity too low
#    if temperature < 50:
#        mail("9259646667@txt.att.net", "Temperature is too low: "+str(temperature))
#        time.sleep(2)
#    if humidity < 50:
#        mail("9259646667@txt.att.net", "Humidity is too low: "+str(humidity))
#       time.sleep(2)
    if (connected):
        try:
            #print("Publishing temp")
            client.publish( 'dvhs_makerspace/feeds/hydro-temp',  payload=str(temperature))
            time.sleep(DELAY_BETWEEN_PUBLISH)
            #print("Publishing humid")
            client.publish( 'dvhs_makerspace/feeds/hydro-humidity', payload=str(humidity))
            time.sleep(DELAY_BETWEEN_PUBLISH)
            #print("Publishing water")
            client.publish( 'dvhs_makerspace/feeds/water-level-cm', payload=str(dist))
            time.sleep(DELAY_BETWEEN_PUBLISH)
        except Exception as e:
            print("Error publishing:" + str(e))
    else:
        print("Not yet connected")
