
from mpu6050 import mpu6050
from driver.vl53l0x_helper import init_vl53l0x
import importlib
from vl53l0x import init_vl53l0xx
from vl53l0x import select_mux_channel
import smbus
import flink
import time
import math
import socket

class RabotAPI:
    
    def __init__(self):
        self.sensorwerte = [0] * 15
        # I2C-Busnummer (je nach Board kann das 0 oder 1 sein, bitte mit `i2cdetect -l` prüfen)
        self.I2C_BUS = 0 # i2c-0 → MIO10/11

        ## -----------mpu6050 Sensor erstellen-----
        self.mpuSensor = mpu6050(0x68, self.I2C_BUS)

        ## -----------Distancesensors------------
        
        self.gpioPins = [0, 1, 2, 3, 4, 5, 6, 7] # GPIO-Pins für XSHUT der VL53L0X-Sensoren

        '''XSHUT über die GPIO's deaktivieren und wieder aktivieren, damit die initialiseirung neu funktioniert.'''
        self.gpio = flink.FlinkGPIO()
        for pin in self.gpioPins:
            self.gpio.setDir(pin, True)
            self.gpio.setValue(pin, False)
            time.sleep(0.02)
            self.gpio.setValue(pin, True)

        self.PA_HUB_I2C_ADDRESS1 = 0x70
        self.PA_HUB_I2C_ADDRESS2 = 0x71

        # Liste der Multiplexer-Kanäle, an denen die VL53L0X-Sensoren angeschlossen sind
        self.Hub1 = [self.PA_HUB_I2C_ADDRESS1, [0, 1, 2, 3]]  # Kanäle für die Sensoren
        self.Hub2 = [self.PA_HUB_I2C_ADDRESS2, [0, 1, 2, 3]]  # Kanäle für die Sensoren am zweiten Hub
        self.Hubs = [self.Hub1, self.Hub2]

        # Initialisiere die ToF-Sensoren über den PA.Hub
        self.tofs = init_vl53l0xx(self.I2C_BUS, self.Hubs)

        ## -----------Motoren------------
        '''
        self.rangeForward = [12, 13]
        self.rangeBackward = [14, 15]

        for pin in self.rangeForward + self.rangeBackward:  # Listen zusammenführen
            self.gpio.setDir(pin, True)
            self.gpio.setValue(pin, False)
        '''

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


        #-----------IP-Adressen------------
        self.left_crawler = "192.168.7.10"
        self.right_crawler = "192.168.7.11"
        self.crawler_ips = [self.left_crawler, self.right_crawler]
        
        self.front_brush = "192.168.7.12"
        self.rear_brush = "192.168.7.13"
        self.brushes_ips = [self.front_brush]           #Nur front brush

        #-----------Crawler-Parameter------------
        self.crawler_rpm = 750
        self.crawler_acc = 5000
        self.crawler_dec = 5000
        self.brake_active = False

        #-----------Brush-Parameter------------
        self.brush_rpm = 1000
        self.brush_acc = 5000
        self.brush_dec = 5000


        
    def getDistSensorValues(self):
        self.bus = smbus.SMBus(self.I2C_BUS)  # I2C-Bus öffnen
        i = 0

        for Hub in self.tofs:
            PA_HUB_I2C_ADDRESS = Hub[0]
            
            muxChanel = 0
            for tof in Hub[1]:
                select_mux_channel(self.bus, muxChanel, PA_HUB_I2C_ADDRESS)  # Wähle den entsprechenden Kanal
                self.sensorwerte[i] = tof.get_distance()
                i += 1
                muxChanel += 1
            self.bus.write_byte(PA_HUB_I2C_ADDRESS, 0x00) # Alle Kanäle am Hub deaktivieren damit Bussprobleme vermieden werden

    
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

    def turn(self, left_speed: int, right_speed: int):
        # Speed range: 100 bis -100. - -> drive backword

        # --- Simulation
        self.stop()  # sicherheitshalber alle Motor-Pins aus
        if left_speed > 0:
            self.gpio.setValue(self.rangeForward[0], True)
        if left_speed < 0:
            self.gpio.setValue(self.rangeBackward[0], True)
        if right_speed > 0:
            self.gpio.setValue(self.rangeForward[1], True)
        if right_speed < 0:
            self.gpio.setValue(self.rangeBackward[1], True)

    def calculate_target_angle(self, direction: str, degree: float) -> float:
        yaw_start = float(self.get_absolute_yaw())

        if direction == "right":
            self.targetAngle = yaw_start - degree
        else:  # left
            self.targetAngle = yaw_start + degree
    
        # Normalize to 0-360 range (handles both positive and negative)
        if self.targetAngle > 0:
            self.targetAngle = self.targetAngle % 360
        else:
            self.targetAngle = 360 - (self.targetAngle % 360)
        
        return self
        
    def stop(self):
        for pin in self.rangeForward + self.rangeBackward:
            self.gpio.setValue(pin, False)

    # Funktionen für REST-Kommunikation mit Motoren
    def send_rest_command(self, ip, index, subindex, hex_value):
        path = f"/od/{index:04X}/{subindex:02X}"
        body = f'"{hex_value}"'
        headers = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {ip}\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )
        try:
            with socket.create_connection((ip, 80), timeout=2) as sock:
                sock.sendall(headers.encode())
                sock.recv(4096)
        except Exception as e:
            print(f"{ip} → Fehler: {e}")

    def read_signed_rpm(self, ip, index, subindex):
        path = f"/od/{index:04X}/{subindex:02X}"
        headers = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {ip}\r\n"
            "Accept: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        try:
            with socket.create_connection((ip, 80), timeout=2) as sock:
                sock.sendall(headers.encode())
                response = sock.recv(4096).decode()
                if '"' in response:
                    hex_value = response.split('"')[1]
                    value = int(hex_value, 16)
                    if value > 0x7FFFFFFF:
                        value -= 0x100000000
                    return value
        except Exception as e:
            print(f"{ip} → Fehler beim Lesen: {e}")
        return None
    
    # Funktionen für Raupensteuerung
    def startup_crawlers(self):     # Raupe Betriebsbereit machen
        self.update_crawler_acc_dcc(self.crawler_acc, self.crawler_dec)
        for ip in self.crawler_ips:
            self.send_rest_command(ip, 0x6060, 0x00, "03")
            self.send_rest_command(ip, 0x6040, 0x00, "0006")
            self.send_rest_command(ip, 0x6040, 0x00, "0007")
            self.send_rest_command(ip, 0x6040, 0x00, "000F")
        time.sleep(0.2)
            
    def close_crawlers(self):       # Raupen abschalten
        self.crawler_stop()
        for ip in self.crawler_ips:
            self.send_rest_command(ip, 0x6040, 0x00, "0006")

    def dec_to_hex_8(self, value):
        return f"{value & 0xFFFFFFFF:08X}"
    
    def update_crawler_acc_dcc(self, acc, dcc): # Aktualisiert Beschleunigung und Verzögerung der Raupen
        self.send_rest_command(self.left_crawler, 0x6083, 0x00, self.dec_to_hex_8(acc))
        self.send_rest_command(self.right_crawler, 0x6083, 0x00, self.dec_to_hex_8(acc))
        self.send_rest_command(self.left_crawler, 0x6084, 0x00, self.dec_to_hex_8(dcc))
        self.send_rest_command(self.right_crawler, 0x6084, 0x00, self.dec_to_hex_8(dcc))

    def crawler_drive(self, rpm):   # Vorwärts und Rückwärts
        self.send_rest_command(self.left_crawler, 0x60FF, 0x00, self.dec_to_hex_8(rpm))
        self.send_rest_command(self.right_crawler, 0x60FF, 0x00, self.dec_to_hex_8(rpm))

    def crawler_stop(self):        # Stoppt die Raupen
        self.crawler_drive(0)

    def crawler_turn_left(self, rpm):
        self.send_rest_command(self.left_crawler, 0x60FF, 0x00, self.dec_to_hex_8(-rpm))
        self.send_rest_command(self.right_crawler, 0x60FF, 0x00, self.dec_to_hex_8(rpm))
    
    def crawler_turn_right(self, rpm):
        self.send_rest_command(self.left_crawler, 0x60FF, 0x00, self.dec_to_hex_8(rpm))
        self.send_rest_command(self.right_crawler, 0x60FF, 0x00, self.dec_to_hex_8(-rpm))


    # Funktionen für Bürstensteuerung
    def startup_brushes(self, rpm = 1000):     # Bürsten starten
        for ip in self.brushes_ips:
            self.send_rest_command(ip, 0x6060, 0x00, "03")
            self.send_rest_command(ip, 0x6040, 0x00, "0006")
            self.send_rest_command(ip, 0x6040, 0x00, "0007")
            self.send_rest_command(ip, 0x6040, 0x00, "000F")
        self.set_brush_rpm(rpm)

    def close_brushes(self):                    # Bürsten stoppen
        self.stop_brushes()
        for ip in self.brushes_ips:
            self.send_rest_command(ip, 0x6040, 0x00, "0006")

    def set_brush_rpm(self, rpm_value):         # Drehzahl der Bürsten einstellen
        for ip in self.brushes_ips:
            self.send_rest_command(ip, 0x60FF, 0x00, self.dec_to_hex_8(rpm_value))
    
    def stop_brushes(self):                     # Bürsten stoppen
        for ip in self.brushes_ips:
            self.send_rest_command(ip, 0x60FF, 0x00, self.dec_to_hex_8(0))
            
