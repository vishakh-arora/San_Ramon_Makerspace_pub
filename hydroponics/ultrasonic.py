#Libraries
import RPi.GPIO as GPIO
import time
from mail import mail
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER_PIN = 18
GPIO_ECHO_PIN = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_PIN, GPIO.OUT)
GPIO.setup(GPIO_ECHO_PIN, GPIO.IN)
 
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

#try:
#	dist = distance()
#	print ("Measured Distance = %.1f cm" % dist)
#finally:
#	GPIO.cleanup()


#if __name__ == '__main__':
#    try:
#        while True:
#            dist = distance()
#            if (dist > 40):
#                print("Sending text")
#                mail("9259646667@txt.att.net", "Refill nutrient solution!: "+str(dist))
#            #print ("Measured Distance = %.1f cm" % dist)
#            time.sleep(1)
#            
# 
        # Reset by pressing CTRL + C
#    except KeyboardInterrupt:
#        print("Measurement stopped by User")
#        GPIO.cleanup()
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
