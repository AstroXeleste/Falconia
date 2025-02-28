import time
import curses
from adafruit_motorkit import MotorKit
from flask import Flask, Response, render_template
import cv2
import pandas as pd
import os
import glob
import RPi.GPIO as GPIO
import threading
from subsystems.humiture_sensor import humiture as hm

# Initialize MotorKit
kit = MotorKit()

# Define motor speed (range: 0 to 1)
DEFAULT_SPEED = -1

def move_forward(speed=DEFAULT_SPEED):
    kit.motor3.throttle = speed
    kit.motor4.throttle = speed

def move_backward(speed=DEFAULT_SPEED):
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

def keyboard_control(stdscr):
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100ms
    stdscr.addstr(0, 0, "Use WASD to move, Q to quit.")

    while True:
        key = stdscr.getch()

        if key == ord('w'):  # Forward
            move_forward()
            stdscr.addstr(1, 0, "Moving Forward  ")
        elif key == ord('s'):  # Backward
            move_backward()
            stdscr.addstr(1, 0, "Moving Backward ")
        elif key == ord('a'):  # Left
            turn_left()
            stdscr.addstr(1, 0, "Turning Left    ")
        elif key == ord('d'):  # Right
            turn_right()
            stdscr.addstr(1, 0, "Turning Right   ")
        elif key == ord('q'):  # Quit
            stop()
            break
        else:
            stop()
            stdscr.addstr(1, 0, "Stopping        ")

# Sensor and data aggregation part
AGGREGATED_CSV_FILE = "/home/x3raspian/Falconia/data_management/data/aggregate.csv"

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

GPIO.setmode(GPIO.BCM)

TRIG = 17
ECHO = 18

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

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
    data = get_latest_data()
    return render_template("index.html", latest_data=data)

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
    distance = round(distance, 2)
    return distance

def read_temp_raw():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
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

def get_latest_data():
    if os.path.exists(AGGREGATED_CSV_FILE):
        try:
            df = pd.read_csv(AGGREGATED_CSV_FILE)
            if not df.empty:
                latest_data = df.iloc[-1].to_dict()
                return latest_data
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return {}
    return {}

def main():
    humiture_sensor = hm.initialize_sensor(hm.DHT_PIN)
    all_data = pd.DataFrame(columns=["Timestamp", "Humiture_Temp_C", "Humiture_Humidity", "Temperature_Temp_C", "Temperature_Temp_F", "Ultrasonic_Distance_CM"])

    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        humiture_temp_c, _, humiture_humidity = hm.read_sensor_data(humiture_sensor)
        temperature_temp_c, temperature_temp_f = read_temp()
        ultrasonic_distance_cm = get_distance()

        if humiture_temp_c is not None:
            new_row = {
                "Timestamp": timestamp,
                "Humiture_Temp_C": humiture_temp_c,
                "Humiture_Humidity": humiture_humidity,
                "Temperature_Temp_C": temperature_temp_c,
                "Temperature_Temp_F": temperature_temp_f,
                "Ultrasonic_Distance_CM": ultrasonic_distance_cm
            }
            print(new_row)
            new_df = pd.DataFrame([new_row])
            all_data = pd.concat([all_data, new_df], ignore_index=True)
            all_data.tail(1).to_csv(AGGREGATED_CSV_FILE, mode='a', header=not os.path.exists(AGGREGATED_CSV_FILE), index=False)
            all_data = all_data.iloc[0:0]
        time.sleep(1)

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

main()

if __name__ == "__main__":
    curses.wrapper(keyboard_control)
