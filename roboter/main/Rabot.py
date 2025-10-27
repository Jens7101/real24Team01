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
                    time.sleep(1)
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

    def rotate180(self, speed, direction):
        Zustand = Enum ('Zustand', ['Turn_180', 'Turned_180'])
        zustand = Zustand.Turn_180
        ProgrammStatus = True
        self.rabot.calibrate_gyro()

        print("Rabot Rotates 180 degrees to the " + direction)

        while ProgrammStatus:
            time.sleep(1 / 1000) # Frequenz in der die Zustände abgefragt werden
            match zustand:
                case Zustand.Turn_180:
                    self.rabot.turn_180(speed, direction)
                    self.rabot.get_absolute_yaw()
                    if self.rabot._yaw >= 178 and self.rabot._yaw <= 182:
                        zustand = Zustand.Turned_180
                        print("Rabot has turned 180 degrees to the " + direction)
                    print(self.rabot._yaw)

                case Zustand.Turned_180:
                    ProgrammStatus = False

                case _:
                    print ("Ungültiger Zustand: " + str(zustand))
        
        self.rabot.stop()
        print("Rabot rotated 180 degrees to the " + direction)




if __name__ == '__main__':
    rabot = Rabot()
    # rabot.test()
    # rabot.drivestraight(-50)
    # rabot.alignApwards()
    rabot.rotate180(50, "right")