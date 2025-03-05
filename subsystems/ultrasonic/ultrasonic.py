import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

TRIG = 24
ECHO = 27

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():

    pulse_start = 0 
    pulse_end = 0

    GPIO.output(TRIG, False)  # Ensure TRIG is low
    time.sleep(0.5)

    GPIO.output(TRIG, True)  # Send a pulse to TRIG
    time.sleep(0.000001)  # Wait for a very short time (microsecond)
    GPIO.output(TRIG, False)

    # Wait for the ECHO pin to go HIGH
    print("Waiting for ECHO to go HIGH")
    while GPIO.input(ECHO) == 0:
        pulse_start = time.perf_counter()

    print("ECHO is HIGH, measuring duration")
    # Wait for the ECHO pin to go LOW
    while GPIO.input(ECHO) == 1:
        pulse_end = time.perf_counter()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Convert to distance in cm
    distance = round(distance, 2)
    return distance

while True:
    try:
        dist = get_distance()
        print("Distance: {} cm".format(dist))
    except Exception as e:
        print("Error:", e)
    time.sleep(1)

# import RPi.GPIO as GPIO
# import time

# GPIO.setmode(GPIO.BCM)

# TRIG = 13
# ECHO = 18

# GPIO.setup(TRIG, GPIO.OUT)
# GPIO.setup(ECHO, GPIO.IN)

# def test_echo():
#     GPIO.output(TRIG, False)
#     time.sleep(2)  # Allow sensor to settle
#     GPIO.output(TRIG, True)
#     time.sleep(0.00001)  # Send pulse
#     GPIO.output(TRIG, False)

#     print("Waiting for echo to go HIGH...")
#     while GPIO.input(ECHO) == 0:
#         print("No ECHO signal")
    
#     print("ECHO HIGH!")
#     while GPIO.input(ECHO) == 1:
#         print("ECHO signal received, waiting for low")

#     print("ECHO LOW!")

# test_echo()
