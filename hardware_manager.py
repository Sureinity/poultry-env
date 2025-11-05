import adafruit_dht
import board
import time
from gpiozero import MotionSensor
import mh_z19
from time import time

# Sensor Initialization
# Initialize DHT22 on GPIO 4
try:
    dht_sensor = adafruit_dht.DHT22(board.D4)
    print("DHT22 Sensor Initialized Successfully.")
except Exception as e:
    dht_sensor = None
    print(f"!!! ERROR: Could not initialize DHT22 sensor. Is it connected? Error: {e}")
    print("!!! INFO: The program will continue with simulated data for Temp/Humidity.")

# Initialize PIR sensor on GPIO 17
try:
    pir_sensor = MotionSensor(17)
    print("PIR Sensor HC-SR501 Initialized Successfully.")
except Exception as e:
    pir_sensor = None
    print(f"!!! ERROR: Could not initialize PIR sensor. Is it connected? Error: {e}")
    print("!!! INFO: The program will continue with simulated data for Motion.")

# Sensor Functions and Classes

def get_environmental_data() -> dict:
    """
    Reads temperature and humidity from the DHT22 sensor.
    Returns a dictionary with 'temperature' and 'humidity' keys.
    Values will be floats on success, or None on failure.
    """
    if dht_sensor is None:
        return {'temperature': None, 'humidity': None}
    try:
        temperature_c = dht_sensor.temperature
        humidity = dht_sensor.humidity
        if temperature_c is not None and humidity is not None:
            return {'temperature': temperature_c, 'humidity': humidity}
        else:
            print("Warning: DHT22 read returned None. Retrying next cycle.")
            return {'temperature': None, 'humidity': None}
    except RuntimeError as error:
        print(f"Warning: DHT22 read failed with RuntimeError: {error.args[0]}")
        return {'temperature': None, 'humidity': None}
    except Exception as error:
        print(f"An unexpected error occurred with the DHT22 sensor: {error}")
        return {'temperature': None, 'humidity': None}

def get_co2_data() -> int | None:
    """
    Reads CO2 concentration from the MH-Z19C sensor.

    Returns:
        int: The CO2 PPM value on success.
        None: On a failed read.
    """
    try:
        co2_data = mh_z19.read()
        if co2_data:
            return co2_data.get('co2')
        else:
            return None
    except Exception as e:
        print(f"An unexpected error occurred with the MH-Z19C sensor: {e}")
        return None

class MotionTracker:
    """
    A stateful class to track and analyze motion data from a PIR sensor.
    """
    def __init__(self, inactivity_threshold_sec: int = 7200):
        self.inactivity_threshold = inactivity_threshold_sec
        self.last_motion_time = time()
        self.motion_now = False

    def update(self):
        """Reads the current state of the PIR sensor and updates the tracker's internal state."""
        if pir_sensor is None:
            self.motion_now = False
            return None
        
        # We need to check pir_sensor.is_active to get the current state
        if pir_sensor.is_active:
            self.motion_now = True
            self.last_motion_time = time()
        else:
            self.motion_now = False

    def get_status(self) -> dict:
        """Analyzes the current state and returns a formatted dictionary for the UI."""
        time_since_last_motion = time() - self.last_motion_time
        
        if time_since_last_motion < 60:
            last_seen_str = "Just now"
        elif time_since_last_motion < 3600:
            last_seen_str = f"{int(time_since_last_motion / 60)} mins ago"
        else:
            last_seen_str = f"{int(time_since_last_motion / 3600)} hours ago"
            
        inactivity_alert = time_since_last_motion > self.inactivity_threshold
        
        return {
            "motion_now": self.motion_now,
            "last_seen_str": last_seen_str,
            "inactivity_alert": inactivity_alert,
            "hyperactivity_alert": False # Placeholder for now
        }

# Standalone Test Block
if __name__ == "__main__":
    print("\n--- Testing Hardware Manager ---")
    motion_tracker = MotionTracker(inactivity_threshold_sec=30) # Short threshold for testing
    
    while True:
        # Test Temp/Humidity
        env_data = get_environmental_data()
        if env_data['temperature'] is not None:
            print(f"Temp/Humidity: {env_data['temperature']:.1f}°C, {env_data['humidity']:.1f}%  |  ", end="")
        else:
            print("Temp/Humidity: FAILED  |  ", end="")
        
        # Test CO2
        co2_value = get_co2_data()
        if co2_value is not None:
            print(f"CO2: {co2_value} ppm | ", end="")
        else:
            print("CO2: FAILED |", end="")

        # Test Motion
        motion_tracker.update()
        motion_status = motion_tracker.get_status()
        print(f"Motion Now: {motion_status['motion_now']} | "
              f"Last Seen: {motion_status['last_seen_str']} | "
              f"Inactivity Alert: {motion_status['inactivity_alert']}")
        
        time.sleep(2)
