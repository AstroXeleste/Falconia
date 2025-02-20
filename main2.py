
import time
import curses
import cv2
import threading
import pandas as pd
import os
import glob
import RPi.GPIO as GPIO
from flask import Flask, Response, render_template
from adafruit_motorkit import MotorKit
from subsystems.humiture_sensor import humiture as hm

# Initialize MotorKit
kit = MotorKit()

# Define motor speed (range: 0 to 1)
DEFAULT_SPEED = 1

def move_backward(speed=DEFAULT_SPEED):
    kit.motor3.throttle = speed
    kit.motor4.throttle = speed

def move_forward(speed=DEFAULT_SPEED):
    kit.motor3.throttle = -speed
    kit.motor4.throttle = -speed

def turn_left(speed=DEFAULT_SPEED):
    kit.motor3.throttle = -speed
    kit.motor4.throttle = speed

def turn_right(speed=DEFAULT_SPEED):
    kit.motor3.throttle = speed
    kit.motor4.throttle = -speed

def stop():
    kit.motor3.throttle = 0
    kit.motor4.throttle = 0

# Flask app for video streaming
app = Flask(__name__)

frameNum = 0

def generate():
    global frameNum
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        frameNum += 1

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Setup GPIO for sensors
GPIO.setmode(GPIO.BCM)
TRIG = 17
ECHO = 18

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# DS18B20 Temperature Sensor Setup
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def get_distance():
    pulse_start = 0 
    pulse_end = 0

    GPIO.output(TRIG, False)
    time.sleep(0.5)

    GPIO.output(TRIG, True)
    time.sleep(0.000001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.perf_counter()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.perf_counter()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def read_temp_raw():
    """Read raw data from DS18B20 sensor."""
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    """Get temperature from the DS18B20 sensor."""
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, round(temp_f, 2)

def sensor_monitor():
    """Continuously read and display sensor data."""
    humiture_sensor = hm.initialize_sensor(hm.DHT_PIN)

    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Read data from Humiture sensor
        humiture_temp_c, _, humiture_humidity = hm.read_sensor_data(humiture_sensor)

        # Read data from DS18B20 temperature sensor
        temperature_temp_c, temperature_temp_f = read_temp()
        ultrasonic_distance_cm = get_distance()

        if humiture_temp_c is not None:
            new_data = {
                "Timestamp": timestamp,
                "Humiture_Temp_C": humiture_temp_c,
                "Humiture_Humidity": humiture_humidity,
                "Temperature_Temp_C": temperature_temp_c,
                "Temperature_Temp_F": temperature_temp_f,
                "Ultrasonic_Distance_CM": ultrasonic_distance_cm
            }
            print(f"Sensor Data: {new_data}")

        time.sleep(1)

def keyboard_control(stdscr):
    stdscr.nodelay(1)
    stdscr.timeout(100)
    stdscr.addstr(0, 0, "Use WASD to move, Q to quit.")

    while True:
        key = stdscr.getch()

        if key == ord('w'):
            move_forward()
            stdscr.addstr(1, 0, "Moving Forward  ")
        elif key == ord('s'):
            move_backward()
            stdscr.addstr(1, 0, "Moving Backward ")
        elif key == ord('a'):
            turn_left()
            stdscr.addstr(1, 0, "Turning Left    ")
        elif key == ord('d'):
            turn_right()
            stdscr.addstr(1, 0, "Turning Right   ")
        elif key == ord('q'):
            stop()
            break
        else:
            stop()
            stdscr.addstr(1, 0, "Stopping        ")

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main():
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start sensor monitoring in a separate thread
    sensor_thread = threading.Thread(target=sensor_monitor)
    sensor_thread.daemon = True
    sensor_thread.start()

    # Run keyboard control in the main thread
    curses.wrapper(keyboard_control)

if __name__ == "__main__":
    main()
