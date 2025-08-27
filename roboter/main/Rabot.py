from enum import Enum
from RabotAPI import *
from Sanduhr import *
import random
import flink
import time

class Rabot:

    def __init__(self):

        '''Stellvertreter Objekt des Roboters erstellen'''
        self.rabot = RabotAPI()

    
    def test (self):
        # Daten auslesen
        print("Beschleunigung:", self.rabot.mpuSensor.get_accel_data())
        print("Gyroskop:", self.rabot.mpuSensor.get_gyro_data())
        print("Temperatur:", self.rabot.mpuSensor.get_temp())
        self.rabot.getDistSensorValues()
        print(self.rabot.sensorwerte)

        




if __name__ == '__main__':
    rabot = Rabot()
    rabot.test()