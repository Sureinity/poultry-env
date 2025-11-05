import time
from gpiozero import InputDevice

# The GPIO pin connected to the KY-037's Digital Output (D0)
SOUND_SENSOR_PIN = 27

try:
    sound_sensor = InputDevice(SOUND_SENSOR_PIN)
except Exception as e:
    print(f"!!! ERROR: Could not initialize sound sensor on GPIO {SOUND_SENSOR_PIN}.")
    print(f"!!! Please check your wiring. Error: {e}")
    exit()

print("--- KY-037 Digital Sound Sensor Test ---")
print("\nThis script will show the raw ON/OFF state of the sensor.")
print("The goal is to physically adjust the blue screw (potentiometer) on the sensor.")
print("Adjust it so the small LED on the module is OFF when it's quiet, and ON when you make noise.")
print("\nPress Ctrl+C to stop.")
print("----------------------------------------------------")

consecutive_sound_events = 0

try:
    while True:
        # sound_sensor.is_active will be True if the pin is HIGH (sound detected)
        # and False if the pin is LOW (quiet).
        if sound_sensor.is_active:
            consecutive_sound_events += 1
            # The '\r' character moves the cursor to the beginning of the line,
            # allowing to overwrite it for a static display.
            print(f"STATUS: SOUND DETECTED! | Consecutive Events: {consecutive_sound_events} | {'#' * consecutive_sound_events}", end='\r')
        else:
            # When it's quiet, reset the counter
            consecutive_sound_events = 0
            # Add spaces at the end to overwrite any previous longer line
            print("STATUS: Quiet...          |                                            ", end='\r')

        # Check the sensor state frequently for responsiveness
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nTest stopped by user.")
