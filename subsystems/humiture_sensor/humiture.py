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


def create_dataframe(data):
    """Creates a Pandas DataFrame from the sensor data."""
    return pd.DataFrame(data)

def append_to_csv(df, file_path):
    """Appends the DataFrame to the CSV file."""
    file_exists = os.path.exists(file_path)
    df.to_csv(file_path, mode='a', header=not file_exists, index=False)

def main():
    """Main function to collect data and write to CSV."""

    sensor = initialize_sensor(DHT_PIN)
    df = pd.DataFrame(columns=["Humidity", "Temperature"])  # Initialize outside the loop

    for _ in range(ITERATIONS):
        temperature_c, temperature_f, humidity = read_sensor_data(sensor)

        if temperature_c is not None:  # Check if data was read successfully
            print(f"Temp={temperature_c:0.1f}ºC, Temp={temperature_f:0.1f}ºF, Humidity={humidity:0.1f}%")

            new_entry = {'Humidity': [humidity], 'Temperature': [temperature_c]}
            df = pd.concat([df, create_dataframe(new_entry)], ignore_index=True)

            # Append to CSV after each reading (more robust)
            append_to_csv(df.tail(1), CSV_FILE_PATH) # Append only the last row for efficiency
            df = df.iloc[0:0] # Clear the df after appending to free up memory

        time.sleep(0.5)

if __name__ == "__main__":
    main()