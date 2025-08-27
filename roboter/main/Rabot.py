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
        self.rabot.getDistSensorValues()
        print(self.rabot.sensorwerte)

        




if __name__ == '__main__':
    rabot = Rabot()
    rabot.test()