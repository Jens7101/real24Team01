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

    def drivestraight(self, speed):

        Zustand = Enum ('Zustand', ['RabotDrive', 'RabotStop'])
        zustand = Zustand.RabotDrive
        ProgrammStatus = True

        self.rabot.drive(speed)
        print("Rabot Drive")

        while ProgrammStatus:
            time.sleep(1 / 1000) # Frequenz in der die Zustände abgefragt werden
            match zustand:
		        
                case Zustand.RabotDrive:
                    time.sleep(4)
                    self.rabot.getDistSensorValues()
                    panelSensors = self.rabot.sensorwerte[0:4]
                    for sensor in panelSensors:
                        print(sensor)
                    for sensor in panelSensors:
                        if sensor < 40:
                            zustand = Zustand.RabotStop
                            print('Rabot Stop')

                case Zustand.RabotStop:
                    self.rabot.stop()
                    ProgrammStatus = False

                case _:
                    print ("Ungültiger Zustand: " + str(zustand))


    def alignApwards(self):

        Zustand = Enum ('Zustand', ['RabotNotAligned', 'RabotAligned'])
        zustand = Zustand.RabotNotAligned
        ProgrammStatus = True

        print("Rabot Aligns Apwards")

        while ProgrammStatus:
            time.sleep(1 / 1000) # Frequenz in der die Zustände abgefragt werden
            match zustand:
                case Zustand.RabotNotAligned:
                    self.rabot.getPitchRoll()
                    print("Pitch: " + str(self.rabot.pitch) + " Roll: " + str(self.rabot.roll))
                    if abs(self.rabot.pitch) < 1:
                        zustand = Zustand.RabotAligned
                        print("Rabot ist ausgerichtet")

                case Zustand.RabotAligned:
                    ProgrammStatus = False

                case _:
                    print ("Ungültiger Zustand: " + str(zustand)) 




if __name__ == '__main__':
    rabot = Rabot()
    # rabot.test()
    # rabot.drivestraight(50)
    rabot.alignApwards()