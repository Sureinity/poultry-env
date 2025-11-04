import csv
import os
import time
import board
import adafruit_dht
from datetime import datetime
from typing import Dict

SENSOR_PIN = board.D4
CSV_FILE = "environment_data.csv"

dht_sensor = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)

def get_environmental_data() -> Dict[str, float | None]:
    """
    Reads temperature and humidity from a DHT22 sensor.
    Logs each reading to a CSV file.
    
    Returns
    -------
    dict:
        On success:
            {'temperature': <float>, 'humidity': <float>}
        On failure:
            {'temperature': None, 'humidity': None}
    """

    # Ensure CSV header exists
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "temperature", "humidity", "status"])

    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity

        if temperature is None or humidity is None:
            print("[WARN] DHT22 returned None values; writing error entry to CSV.")
            _log_to_csv(None, None, "error")
            return {'temperature': None, 'humidity': None}

        print(f"[INFO] DHT22 Read Successful — Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}%")

        _log_to_csv(temperature, humidity, "ok")
        return {'temperature': temperature, 'humidity': humidity}

    except RuntimeError as e:
        # Common transient sensor errors
        print(f"[ERROR] DHT22 transient failure: {e.args[0]}")
        _log_to_csv(None, None, "runtime_error")
        return {'temperature': None, 'humidity': None}

    except Exception as e:
        # Hardware or fatal error
        print(f"[CRITICAL] Unexpected DHT22 failure: {e}")
        _log_to_csv(None, None, f"exception:{type(e).__name__}")
        dht_sensor.exit()
        raise


def _log_to_csv(temperature: float | None, humidity: float | None, status: str):
    """Append one record to the CSV log."""
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(timespec='seconds'),
            temperature if temperature is not None else "",
            humidity if humidity is not None else "",
            status
        ])


# Example usage (e.g., inside a Textual worker loop)
if __name__ == "__main__":
    while True:
        data = get_environmental_data()
        print(data)
        time.sleep(5)

