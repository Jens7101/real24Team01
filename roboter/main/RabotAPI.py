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

        ## -----------_Yaw Tracking------------
        # Gyro bias (deg/s)
        self.gyro_bias = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        # Yaw state: keep _yaw as degrees for compatibility with Rabot.rotate180
        self._yaw_rad = 0.0
        self._yaw = 0.0
        self._last_time = time.time()
        # Pitch/Roll in degrees (used elsewhere in your code)
        self.pitch = 0.0
        self.roll = 0.0
        # Kalibriere das Gyroskop beim Start
        self.calibrate_gyro()

        
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
        
    def calibrate_gyro(self, samples: int = 200, delay: float = 0.01):
        """
        Measure gyro bias (deg/s). Call while MPU is stationary.
        """
        sx = sy = sz = 0.0
        for _ in range(samples):
            g = self.mpuSensor.get_gyro_data()
            sx += g['x']
            sy += g['y']
            sz += g['z']
            time.sleep(delay)
        self.gyro_bias['x'] = sx / samples
        self.gyro_bias['y'] = sy / samples
        self.gyro_bias['z'] = sz / samples

    ''' 
    zweite varsion der getPitchRoll funktion ohne komplementärfilter
    löschen wenn rest funtioniert
    --------------

    def getPitchRoll(self):
        """
        Reads accelerometer and computes pitch and roll (in degrees).
        Stores self.pitch and self.roll (degrees).
        """
        accel = self.mpuSensor.get_accel_data()
        ax, ay, az = accel['x'], accel['y'], accel['z']

        # compute roll and pitch (radians)
        roll_rad = math.atan2(ay, az)
        pitch_rad = math.atan2(-ax, math.sqrt(ay * ay + az * az))

        # store degrees for compatibility
        self.roll = math.degrees(roll_rad)
        self.pitch = math.degrees(pitch_rad)

        return self.pitch, self.roll
        '''

    def get_absolute_yaw(self):
        """
        Integrate tilt-compensated yaw rate to obtain yaw in degrees.
        Uses gyro bias subtraction and pitch/roll from accel.
        Updates self._yaw (degrees).
        """
        now = time.time()
        dt = now - getattr(self, '_last_time', now)
        if dt <= 0:
            dt = 1e-6
        self._last_time = now

        # update pitch/roll
        self.getPitchRoll()
        roll_rad = math.radians(self.roll)
        pitch_rad = math.radians(self.pitch)

        # read gyro (assumed in deg/s), subtract bias, convert to rad/s
        g = self.mpuSensor.get_gyro_data()
        gx = math.radians(g['x'] - self.gyro_bias['x'])
        gy = math.radians(g['y'] - self.gyro_bias['y'])
        gz = math.radians(g['z'] - self.gyro_bias['z'])

        # compute yaw rate (psi_dot) from body rates using Euler relation:
        # psi_dot = sin(phi)/cos(theta) * q + cos(phi)/cos(theta) * r
        # where p=gx, q=gy, r=gz and phi=roll, theta=pitch
        cos_pitch = math.cos(pitch_rad)
        if abs(cos_pitch) < 1e-3:
            # Gimbal lock: skip update to avoid large errors
            return self._yaw

        psi_dot = (math.sin(roll_rad) / cos_pitch) * gy + (math.cos(roll_rad) / cos_pitch) * gz

        # integrate (yaw in radians)
        self._yaw_rad += psi_dot * dt
        # normalize to [0,360)
        self._yaw = (math.degrees(self._yaw_rad)) % 360.0

        return self._yaw

    def reset_yaw(self):
        self._yaw_rad = 0.0
        self._yaw = 0.0
        self._last_time = time.time()


    def drive(self, speed: int):
        # Speed range: 100 bis -100. - -> drive backword

        # --- Simulation
        if speed > 0:
            for pin in self.rangeForward:
                self.gpio.setValue(pin, True)
        if speed < 0:
            for pin in self.rangeBackward:
                self.gpio.setValue(pin, True)


    def turn_left(self, speed):
        # accept only non-negative speed
        if speed < 0:
            print("value for speed is not in the allowed range")
            return

        # optional: sicherheitshalber alle Motor-Pins aus
        for pin in self.rangeForward + self.rangeBackward:
            self.gpio.setValue(pin, False)

        # Linksdrehung: rechter Motor vorwärts, linker Motor rückwärts
        self.gpio.setValue(self.rangeForward[1], True)
        self.gpio.setValue(self.rangeBackward[0], True)

    def turn_right(self, speed):
        # accept only non-negative speed
        if speed < 0:
            print("value for speed is not in the allowed range")
            return

        # sicherheitshalber alle Motor-Pins aus
        for pin in self.rangeForward + self.rangeBackward:
            self.gpio.setValue(pin, False)

        # Rechtsdrehung: rechter Motor rückwärts, linker Motor vorwärts
        self.gpio.setValue(self.rangeBackward[1], True)
        self.gpio.setValue(self.rangeForward[0], True)

    def turn_Degree(self, speed, direction , target):
        self.turn_degree_done = False

        if speed < 0:
            print("value vor speed is not in the allowed range")
        else:
            
            if direction == "left":
                self.turn_left(speed)
            
            elif direction == "right":
                self.turn_right(speed)

            else:
                print("direction must be 'left' or 'right'")

            if target -1 < self.get_absolute_yaw() < target +1:
                self.turn_degree_done = True

    def calculate_target_angle(self, direction: str, degree: float) -> float:
        yaw_start = float(self.get_absolute_yaw())

        if direction == "right":
            target = yaw_start - degree
        else:  # left
            target = yaw_start + degree
    
        # Normalize to 0-360 range (handles both positive and negative)
        if target > 0:
            target = target % 360
        else:
            target = 360 + (target % 360)
        
        return target
        
    def stop(self):
        for pin in self.rangeForward + self.rangeBackward:
            self.gpio.setValue(pin, False)
    






