from time import sleep
from mpu6050 import mpu6050
import smbus

# Verwende den korrekten Bus (prüfe mit: ls /dev/i2c-*)
bus_num = 0  # i2c-0 → MIO10/11

# Sensor initialisieren mit explizitem Bus
sensor = mpu6050(0x68, bus=bus_num)
i = 0

while i < 100:
    # Daten auslesen
    print("Beschleunigung:", sensor.get_accel_data())
    print("Gyroskop:", sensor.get_gyro_data())
    print("Temperatur:", sensor.get_temp())
    sleep(2)
