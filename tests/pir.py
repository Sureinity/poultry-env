from gpiozero import MotionSensor

pir = MotionSensor(17)

while True:
    pir.wait_for_motion()
    print("Motion Detected")
    sleep(1)
