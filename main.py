# from subsystems.humiture_sensor import humiture as hm
# import time
# import pandas as pd
# import os
# import glob

# import RPi.GPIO as GPIO
# import time

# AGGREGATED_CSV_FILE = "/home/x3raspian/Falconia/data_management/data/aggregate.csv"

# # Initialize the DS18B20 temperature sensor
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

# base_dir = '/sys/bus/w1/devices/'
# device_folder = glob.glob(base_dir + '28*')[0]
# device_file = device_folder + '/w1_slave'

# GPIO.setmode(GPIO.BCM)

# TRIG = 17
# ECHO = 18

# GPIO.setup(TRIG, GPIO.OUT)
# GPIO.setup(ECHO, GPIO.IN)

# # Temperature Sensor

# def get_distance():

#     pulse_start = 0 
#     pulse_end = 0

#     GPIO.output(TRIG, False)  # Ensure TRIG is low
#     time.sleep(0.5)

#     GPIO.output(TRIG, True)  # Send a pulse to TRIG
#     time.sleep(0.000001)  # Wait for a very short time (microsecond)
#     GPIO.output(TRIG, False)

#     # Wait for the ECHO pin to go HIGH
#     # print("Waiting for ECHO to go HIGH")
#     while GPIO.input(ECHO) == 0:
#         pulse_start = time.perf_counter()

#     # print("ECHO is HIGH, measuring duration")
#     # Wait for the ECHO pin to go LOW
#     while GPIO.input(ECHO) == 1:
#         pulse_end = time.perf_counter()

#     pulse_duration = pulse_end - pulse_start
#     distance = pulse_duration * 17150  # Convert to distance in cm
#     distance = round(distance, 2)
#     return distance

# # Temperature Sensor
# def read_temp_raw():
#     """Read raw data from DS18B20 sensor."""
#     f = open(device_file, 'r')
#     lines = f.readlines()
#     f.close()
#     return lines

# def read_temp():
#     """Get temperature from the DS18B20 sensor."""
#     lines = read_temp_raw()
#     while lines[0].strip()[-3:] != 'YES':
#         time.sleep(0.2)
#         lines = read_temp_raw()
#     equals_pos = lines[1].find('t=')
#     if equals_pos != -1:
#         temp_string = lines[1][equals_pos + 2:]
#         temp_c = float(temp_string) / 1000.0
#         temp_f = temp_c * 9.0 / 5.0 + 32.0
#         return temp_c, round(temp_f, 2)

# def main():
#     # Initialize the humiture sensor
#     humiture_sensor = hm.initialize_sensor(hm.DHT_PIN)
    
#     all_data = pd.DataFrame(columns=["Timestamp", "Humiture_Temp_C", "Humiture_Humidity", "Temperature_Temp_C", "Temperature_Temp_F"])
    
#     while True:
#         timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
        
#         # Read data from the Humiture sensor
#         humiture_temp_c, _, humiture_humidity = hm.read_sensor_data(humiture_sensor)
        
#         # Read data from the DS18B20 temperature sensor
#         temperature_temp_c, temperature_temp_f = read_temp()
#         ultrasonic_distance_cm = get_distance()


#         if humiture_temp_c is not None:  # Check if humiture data was read successfully
#             new_row = {
#                 "Timestamp": timestamp,
#                 "Humiture_Temp_C": humiture_temp_c,
#                 "Humiture_Humidity": humiture_humidity,
#                 "Temperature_Temp_C": temperature_temp_c,
#                 "Temperature_Temp_F": temperature_temp_f,
#                 "Ultrasonic_Distance_CM": ultrasonic_distance_cm
#             }

#             print(new_row)

#             new_df = pd.DataFrame([new_row])  # Create dataframe from dictionary
#             all_data = pd.concat([all_data, new_df], ignore_index=True)

#             # Append to CSV after each reading
#             all_data.tail(1).to_csv(AGGREGATED_CSV_FILE, mode='a', header=not os.path.exists(AGGREGATED_CSV_FILE), index=False)
#             all_data = all_data.iloc[0:0]  # Clear the dataframe for memory management

#         time.sleep(1)  # Adjust sleep time as needed

# # Start the main function
# main()

from flask import Flask, Response, render_template
import cv2
import time
import pandas as pd
import os
import glob
import RPi.GPIO as GPIO
import threading  # To run the Flask server in a separate thread

from subsystems.humiture_sensor import humiture as hm

AGGREGATED_CSV_FILE = "/home/x3raspian/Falconia/data_management/data/aggregate.csv"

# Initialize the DS18B20 temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

GPIO.setmode(GPIO.BCM)

TRIG = 24
ECHO = 27

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)



# Initialize Flask app for video streaming
app = Flask(__name__)

frameNum = 0  # Initialize frame number

# Camera capture function
def generate():
    global frameNum
    cap = cv2.VideoCapture(0)  # Use the default camera, or specify your camera here

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
    return render_template("index.html")  # Ensure you have an "index.html" template

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def get_distance():
    pulse_start = 0 
    pulse_end = 0

    GPIO.output(TRIG, False)  # Ensure TRIG is low
    time.sleep(0.5)

    GPIO.output(TRIG, True)  # Send a pulse to TRIG
    time.sleep(0.000001)  # Wait for a very short time (microsecond)
    GPIO.output(TRIG, False)

    # Wait for the ECHO pin to go HIGH
    while GPIO.input(ECHO) == 0:
        pulse_start = time.perf_counter()

    # Wait for the ECHO pin to go LOW
    while GPIO.input(ECHO) == 1:
        pulse_end = time.perf_counter()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Convert to distance in cm
    distance = round(distance, 2)
    return distance

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

def main():
    # Initialize the humiture sensor
    humiture_sensor = hm.initialize_sensor(hm.DHT_PIN)
    
    all_data = pd.DataFrame(columns=["Timestamp", "Humiture_Temp_C", "Humiture_Humidity", "Temperature_Temp_C", "Temperature_Temp_F"])

    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
        
        # Read data from the Humiture sensor
        humiture_temp_c, _, humiture_humidity = hm.read_sensor_data(humiture_sensor)
        
        # Read data from the DS18B20 temperature sensor
        temperature_temp_c, temperature_temp_f = read_temp()

        if humiture_temp_c is not None:  # Check if humiture data was read successfully
            new_row = {
                "Timestamp": timestamp,
                "Humiture_Temp_C": humiture_temp_c,
                "Humiture_Humidity": humiture_humidity,
                "Temperature_Temp_C": temperature_temp_c,
                "Temperature_Temp_F": temperature_temp_f,
                "Ultrasonic_Distance_CM": 1000
            }

            print(new_row)

            new_df = pd.DataFrame([new_row])  # Create dataframe from dictionary
            all_data = pd.concat([all_data, new_df], ignore_index=True)

            # Append to CSV after each reading
            all_data.tail(1).to_csv(AGGREGATED_CSV_FILE, mode='a', header=not os.path.exists(AGGREGATED_CSV_FILE), index=False)
            all_data = all_data.iloc[0:0]  # Clear the dataframe for memory management

        time.sleep(1)  # Adjust sleep time as needed

# Function to run Flask app in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# Start the Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Start the main function to handle sensor readings and data aggregation
main()
