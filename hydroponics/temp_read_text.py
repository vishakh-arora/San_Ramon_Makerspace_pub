#fout = open("temp_data.txt", "a")
import Adafruit_DHT

#while True:

humidity, temperature = Adafruit_DHT.read_retry(11, 4)
temperature = (temperature*(5/9))+32
#fout.write('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity)+"\n")
printf('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity)+"\n")
