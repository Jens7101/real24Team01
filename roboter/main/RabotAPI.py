from Distance_Sensoren import*
from mpu6050 import mpu6050
from driver.vl53l0x_helper import init_vl53l0x


class RabotAPI:
    
    def __init__(self):
        self.sensorwerte = [0] * 10

        ## mpu6050 Sensor erstellen
        self.mpuSensor = mpu6050(0x68)
        
    def getDistSensorValues(self):
        for i in range(len(werte)):  # bisher: range (16)
            self.sensorwerte[i] = int(werte[i])
        self.protokollieren(auftrag, antwort)



