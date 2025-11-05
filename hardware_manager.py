import adafruit_dht
import board
import time
from gpiozero import MotionSensor, InputDevice
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

# Initialize KY-037 Soun Sensor on GPIO 27
try:
    sound_sensor = InputDevice(27)
    print("Sound Sensor KY-037 Initialized Successfully.")
except Exception as e:
    sound_sensor = None
    print(f"!!! ERROR: Could not initialize Sound Sensor. Is it connected? Error: {e}")

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

class SoundDisturbanceDetector:
    """
    A stateful class to analyze the digital output of a KY-037 sound sensor.
    Implements a heuristic algorithm to filter brief noises and detect sustained disturbances.
    """
    def __init__(self, sustained_noise_sec: int = 8, quiet_reset_sec: int = 3):
        self.sustained_noise_duration = sustained_noise_sec
        self.quiet_reset_duration = quiet_reset_sec
        
        self.noise_start_time = None
        self.quiet_start_time = time()
        self.alert_triggered_for_event = False
        self.sound_is_active = False

    def update(self):
        """Reads the sensor and updates the internal state. Should be called every loop."""
        if sound_sensor is None:
            self.sound_is_active = False
            return
            
        self.sound_is_active = sound_sensor.is_active

        if self.sound_is_active:
            # Noise is detected
            self.quiet_start_time = None # It's not quiet, so reset the quiet timer
            if self.noise_start_time is None:
                # This is the beginning of a new noise event
                self.noise_start_time = time()
        else:
            # It is quiet
            self.noise_start_time = None # It's not noisy, so reset the noise timer
            if self.quiet_start_time is None:
                # This is the beginning of a new quiet period
                self.quiet_start_time = time()

            # If it's been quiet for long enough, reset the alert flag
            if time() - self.quiet_start_time > self.quiet_reset_duration:
                self.alert_triggered_for_event = False

    def get_status(self) -> dict:
        """Applies the heuristic and returns the current status."""
        alert_now = False
        
        # Check for a sustained noise event
        if self.noise_start_time is not None:
            noise_duration = time() - self.noise_start_time
            if noise_duration > self.sustained_noise_duration and not self.alert_triggered_for_event:
                alert_now = True
                self.alert_triggered_for_event = True # Latch the alert until it gets quiet

        return {
            "sound_now": self.sound_is_active,
            "acoustic_alert": alert_now,
        }


# Standalone Test Block
if __name__ == "__main__":
    print("\n--- Testing Hardware Manager ---")
    motion_tracker = MotionTracker(inactivity_threshold_sec=30) # Short threshold for testing
    sound_detector = SoundDisturbanceDetector(sustained_noise_sec=5, quiet_reset_sec=2) # Short threshold for testing
    
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
        
        # Test Sound
        sound_detector.update()
        sound_status = sound_detector.get_status()
        print(f"Sound Now: {sound_status['sound_now']} | "
              f"Acoustic Alert: {sound_status['acoustic_alert']}")
        
        time.sleep(1)
