import mh_z19
import time

print("--- MH-Z19C CO2 Sensor Test Script ---")
print("Reading data every 5 seconds. Press Ctrl+C to stop.")
print("If you see 'Failed to read', please double-check your wiring and ensure the serial console is disabled in raspi-config.")
print("----------------------------------------------------")

try:
    while True:
        # The .read() function handles all the complex serial communication.
        # It automatically handles checksums to ensure the data is valid.
        co2_data = mh_z19.read()

        # On a successful read, co2_data will be a dictionary like {'co2': 550}
        # On a failed read (e.g., bad wiring, sensor not ready), it will be None.
        if co2_data:
            # Safely get the 'co2' value from the dictionary
            co2_ppm = co2_data.get('co2')
            
            print(f"CO2 Concentration: {co2_ppm} ppm")
            
            # You can test if the sensor is responsive by breathing near it.
            # The CO2 level should spike significantly.

        else:
            print("Failed to read from sensor. Please check wiring and configuration.")

        # Wait for 5 seconds before the next reading.
        time.sleep(5)

except KeyboardInterrupt:
    print("\nProgram stopped by user.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
    print("Please ensure the hardware is connected correctly and prerequisites are met.")
