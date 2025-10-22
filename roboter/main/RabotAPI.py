from Distance_Sensoren import*
from mpu6050 import mpu6050
from driver.vl53l0x_helper import init_vl53l0x
import importlib
from vl53l0x import init_vl53l0xx
from vl53l0x import select_mux_channel
import smbus
import flink
import time
import math


class RabotAPI:
    
    def __init__(self):
        self.sensorwerte = [0] * 10
        # I2C-Busnummer (je nach Board kann das 0 oder 1 sein, bitte mit `i2cdetect -l` prüfen)
        self.I2C_BUS = 0 # i2c-0 → MIO10/11

        ## -----------mpu6050 Sensor erstellen-----
        self.mpuSensor = mpu6050(0x68, self.I2C_BUS)

        ## -----------Distancesensors------------
        

        # Liste der Multiplexer-Kanäle, an denen die VL53L0X-Sensoren angeschlossen sind
        self.MUX_CHANNELS = [0, 1, 2, 3]  # Beispiel: Sensoren an Kanal 0 und 1 des PA.Hub

        '''XSHUT über die GPIO's deaktivieren und wieder aktivieren, damit die initialiseirung neu funktioniert.'''
        self.gpio = flink.FlinkGPIO()
        for pin in self.MUX_CHANNELS:
            self.gpio.setDir(pin, True)
            self.gpio.setValue(pin, False)
            time.sleep(0.01)
            self.gpio.setValue(pin, True)

        # Initialisiere die ToF-Sensoren über den PA.Hub
        self.tofs = init_vl53l0xx(self.I2C_BUS, self.MUX_CHANNELS)

        ## -----------Motoren------------
        self.rangeForward = [12, 13]
        self.rangeBackward = [14, 15]

        for pin in self.rangeForward + self.rangeBackward:  # Listen zusammenführen
            self.gpio.setDir(pin, True)
            self.gpio.setValue(pin, False)

        
    def getDistSensorValues(self):
        self.bus = smbus.SMBus(self.I2C_BUS)  # I2C-Bus öffnen
        i = 0
        muxChanel = 0

        for tof in self.tofs:
            select_mux_channel(self.bus, self.MUX_CHANNELS[muxChanel])
            self.sensorwerte[i] = tof.get_distance()
            i += 1
            muxChanel += 1

    def getPitchRoll(self):
        dt = 0.02  # Abtastzeit (20 ms → 50 Hz)
        alpha = 0.98  # Filterkonstante

        # Anfangswerte aus Beschleunigung
        accel = self.mpuSensor.get_accel_data()
        ax, ay, az = accel['x'], accel['y'], accel['z']
        roll = math.degrees(math.atan2(ay, az))
        pitch = math.degrees(math.atan2(-ax, math.sqrt(ay**2 + az**2)))

        # Gyroskopdaten
        gyro = self.mpuSensor.get_gyro_data()
        gx, gy, gz = gyro['x'], gyro['y'], gyro['z']

        # Integriere Gyro-Daten
        roll_gyro = roll + gx * dt
        pitch_gyro = pitch + gy * dt

        # Beschleunigungsdaten
        accel = self.mpuSensor.get_accel_data()
        ax, ay, az = accel['x'], accel['y'], accel['z']
        roll_acc = math.degrees(math.atan2(ay, az))
        pitch_acc = math.degrees(math.atan2(-ax, math.sqrt(ay**2 + az**2)))

        # Komplementärfilter
        roll = alpha * roll_gyro + (1 - alpha) * roll_acc
        pitch = alpha * pitch_gyro + (1 - alpha) * pitch_acc

        self.roll = roll
        self.pitch = pitch


    def drive(self, speed: int):
        # Speed range: 100 bis -100. - -> drive backword

        # --- Simulation
        if speed > 0:
            for pin in self.rangeForward:
                self.gpio.setValue(pin, True)
        if speed < 0:
            for pin in self.rangeBackward:
                self.gpio.setValue(pin, True)

    def stop(self):
        for pin in self.rangeForward + self.rangeBackward:
            self.gpio.setValue(pin, False)
    






