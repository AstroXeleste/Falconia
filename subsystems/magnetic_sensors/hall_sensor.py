#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

ReedPin = 11  # Pin for the reed switch

def setup():
    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    GPIO.setup(ReedPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set ReedPin mode as input with pull-up resistor

def detect():
    # Continuously print a message when reed switch detects the magnet or not
    if GPIO.input(ReedPin) == GPIO.LOW:
        print("Magnet detected!")
    else:
        print("Magnet removed!")

def loop():
    while True:
        detect()  # Continuously check the reed switch state
        time.sleep(0.5)  # Add a small delay to prevent excessive printing (0.5 second)

def destroy():
    GPIO.cleanup()  # Release GPIO resources

if __name__ == '__main__':  # Program starts from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy function will be executed
        destroy()
