import time
import board
import adafruit_dht
import pandas as pd
import os

# Sensor data pin
DHT_PIN = board.D5

# CSV file path
CSV_FILE_PATH = "/home/x3raspian/Falconia/data_management/data/humitureData.csv"

# Number of iterations to collect data
ITERATIONS = 30

def initialize_sensor(pin):
    """Initializes the DHT sensor."""
    return adafruit_dht.DHT11(pin)

def read_sensor_data(sensor):
    """Reads temperature and humidity from the sensor."""
    try:
        temperature_c = sensor.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = sensor.humidity
        return temperature_c, temperature_f, humidity
    except RuntimeError as error:
        print(f"Error reading sensor: {error.args[0]}")
        return None, None, None  # Return None values to indicate failure
    except Exception as error:
        sensor.exit()
        raise error

sensor = initialize_sensor(DHT_PIN)
print(sensor)
print(sensor.temperature)
