import Adafruit_DHT
import time

while True:
    humidity, temperature = Adafruit_DHT.read_retry(11, 4) #read from Adafruit DHT11 sensor, GPIO pin 4
    temperature = (temperature*(9.0/5))+32
    print("Temperature: " + str(temperature)+" Humidity: "+str(humidity))
    time.sleep(1)
