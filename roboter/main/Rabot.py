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
                    self.rabot.stop()
                    ProgrammStatus = False

                case _:
                    print ("Ungültiger Zustand: " + str(zustand))

    def rotate(self, speed, direction, degree):
        Zustand = Enum ('Zustand', ['Turn', 'Turned'])
        
        target = self.rabot.calculate_target_angle(direction, degree)
        self.rabot.turn_Degree(speed, direction, target)

        zustand = Zustand.Turn
        ProgrammStatus = True
        
        print("Rabot Rotates", str(degree),  "degrees to the " + direction)

        while ProgrammStatus:
            time.sleep(1 / 1000) # Frequenz in der die Zustände abgefragt werden
            match zustand:
                case Zustand.Turn:
                    self.rabot.turn_Degree(speed, direction, target)
                    print(self.rabot._yaw)
                    print("Target:", target)
                    if self.rabot.turn_degree_done:
                        zustand = Zustand.Turned
                        print("Rabot has rotated", str(degree),  "degrees to the " + direction)

                case Zustand.Turned:
                    self.rabot.stop()
                    ProgrammStatus = False

                case _:
                    print ("Ungültiger Zustand: " + str(zustand))

    def first_demo_programm(self):
        Zustand = Enum ('Zustand', ['RobiDrehtBisHorizontal', 'RobiFährVorwärts1',
            'RobiAusrichten', 'RobiVierteldrehungLinks1', 'RobiFährtVorwärts2',
            'RobiDreht180', 'ViertelDrehungRechts_Zy', 'RobiFährtRunter_Zy',
            'ViertelDrehungLinks_Zy', 'RobiFährtVorwärts_Zy', 'RobiStoppt',
            "RobiFährtVorwärtsLetzteReihe"])
        self.rabot.getPitchRoll()
        zustand = Zustand.RobiDrehtBisHorizontal
        ProgrammStatus = True

        if abs(self.rabot.pitch) <= 0:
            self.rabot.turn_left(30)
            print("Rabot dreht links")
        elif abs(self.rabot.pitch) > 0:
            self.rabot.turn_right(30)
            print("Rabot dreht rechts")


        while ProgrammStatus:
            time.sleep(1 / 1000) # Frequenz in der die Zustände abgefragt werden
            match zustand:
                case Zustand.RobiDrehtBisHorizontal:
                    self.rabot.getPitchRoll()
                    print("Pitch: " + str(self.rabot.pitch))
                    if abs(self.rabot.pitch) < 1:
                        zustand = Zustand.RobiFährVorwärts1
                        self.rabot.drive(50)
                        print("Rabot fährt vorwärts")

                case Zustand.RobiFährVorwärts1:
                    time.sleep(1)
                    self.rabot.getDistSensorValues()
                    frontSensors = self.rabot.sensorwerte[0:1]

                    if frontSensors[0] < 30:
                        self.rabot.stop()
                        zustand = Zustand.RobiAusrichten
                        self.rabot.turn(0, 30)
                    elif frontSensors[1] < 30:
                        self.rabot.stop()
                        zustand = Zustand.RobiAusrichten
                        self.rabot.turn(30, 0)

                    print("Rabor richtet sich aus")  

                case Zustand.RobiAusrichten:
                    self.rabot.getDistSensorValues()
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] >= 30 and frontSensors[1] >= 30:
                        zustand = Zustand.RobiVierteldrehungLinks1
                        self.rabot.stop()
                        target = self.rabot.calculate_target_angle("left", 90)
                        self.rabot.turn_Degree(30, "left", target)
                        print("Rabot macht eine Vierteldrehung nach links")

                case Zustand.RobiVierteldrehungLinks1:
                    if self.rabot.turn_degree_done:
                        zustand = Zustand.RobiFährtVorwärts2
                        self.rabot.drive(50)
                        Vorwärts = 1
                        print("Rabot fährt vorwärts")

                case Zustand.RobiFährtVorwärts2:
                    self.rabot.getDistSensorValues()
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] < 30 or frontSensors[1] < 30:
                        self.rabot.stop()

                        if Vorwärts == 1:
                            zustand = Zustand.RobiDreht180
                            # Parameter für 180 Grad Drehung
                            Vorwärts = 2
                            # Rabot dreht sich um 180 Grad
                            target = self.rabot.calculate_target_angle("left", 180)
                            self.rabot.turn_Degree(30, "left", target)
                            print("Rabot dreht sich um 180 Grad")

                        if Vorwärts == 2:
                            zustand = Zustand.ViertelDrehungRechts_Zy
                            # Parameter für Zyklus
                            Drehen = 1
                            rechtsLinks = "right"
                            lastRow = False
                            # Rabot macht eine Vierteldrehung nach rechts
                            target = self.rabot.calculate_target_angle("right", 90)
                            self.rabot.turn_Degree(30, "right", target)
                            print("Rabot macht eine Vierteldrehung nach rechts")

                case Zustand.RobiDreht180:
                    if self.rabot.turn_degree_done:
                        zustand = Zustand.RobiFährtVorwärts2
                        print("Rabot hat sich um 180 Grad gedreht")
                    pass

                case Zustand.ViertelDrehungRechts_Zy:
                    if self.rabot.turn_degree_done:
                        
                        if Drehen == 1:
                            zustand = Zustand.RobiFährtRunter_Zy
                            self.rabot.drive(50)
                            print("Rabot fährt runter")
                        elif Drehen == 2:
                            zustand = Zustand.RobiFährtVorwärts_Zy
                            # Parameter für Zyklus
                            rechtsLinks = "left"
                            self.rabot.drive(50)
                            print("Rabot fährt geradeaus")
                        elif lastRow == True:
                            zustand = Zustand.RobiFährtVorwärtsLetzteReihe
                            self.rabot.drive(50)
                            print("Rabot fährt die letzte Reihe vorwärts")



                case Zustand.RobiFährtRunter_Zy:
                    time.sleep(2)
                    self.rabot.getDistSensorValues()
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] < 30 or frontSensors[1] < 30:
                        if rechtsLinks == "left":
                            self.rabot.stop()
                            zustand = Zustand.ViertelDrehungLinks_Zy
                            # Parameter für Zyklus
                            lastRow = True
                            target = self.rabot.calculate_target_angle("left", 90)
                            self.rabot.turn_Degree(30, "left", target)
                            print("Rabot macht eine Vierteldrehung nach links")
                        elif rechtsLinks == "right":
                            self.rabot.stop()
                            zustand = zustand.ViertelDrehungRechts_Zy
                            # Parameter für Zyklus
                            lastRow = True
                            target = self.rabot.calculate_target_angle("right", 90)
                            self.rabot.turn_Degree(30, "right", target)
                            print("Rabot macht eine Vierteldrehung nach rechts")

                    elif rechtsLinks == "left":
                        zustand = Zustand.ViertelDrehungLinks_Zy
                        Drehen = 2
                        target = self.rabot.calculate_target_angle("left", 90)
                        self.rabot.turn_Degree(30, "left", target)
                        print("Rabot macht eine Vierteldrehung nach links")

                    elif rechtsLinks == "right":
                        zustand = Zustand.ViertelDrehungRechts_Zy
                        Drehen = 2
                        target = self.rabot.calculate_target_angle("right", 90)
                        self.rabot.turn_Degree(30, "right", target)
                        print("Rabot macht eine Vierteldrehung nach rechts")    

                case Zustand.ViertelDrehungLinks_Zy:
                    if self.rabot.turn_degree_done:
                        
                        if Drehen == 1:
                            zustand = Zustand.RobiFährtRunter_Zy
                            self.rabot.drive(50)
                            print("Rabot fährt runter")
                        elif Drehen == 2:
                            zustand = Zustand.RobiFährtVorwärts_Zy
                            # Parameter für Zyklus
                            rechtsLinks = "rechts"
                            # Rabot fährt geradeaus
                            self.rabot.drive(50)
                            print("Rabot fährt geradeaus")
                        elif lastRow == True:
                            zustand = Zustand.RobiFährtVorwärtsLetzteReihe
                            self.rabot.drive(50)
                            print("Rabot fährt die letzte Reihe vorwärts")

                case Zustand.RobiFährtVorwärts_Zy:
                    rabot.getDistSensorValues()
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] < 30 or frontSensors[1] < 30:
                        self.rabot.stop()

                        if rechtsLinks == "left":
                            zustand = Zustand.ViertelDrehungLinks_Zy
                            # Parameter für Zyklus
                            Drehen = 1
                            # Rabot macht eine Vierteldrehung nach links
                            target = self.rabot.calculate_target_angle("left", 90)
                            self.rabot.turn_Degree(30, "left", target)
                            print("Rabot macht eine Vierteldrehung nach links")
                        elif rechtsLinks == "right":
                            zustand = Zustand.ViertelDrehungRechts_Zy
                            # Parameter für Zyklus
                            Drehen = 1
                            # Rabot macht eine Vierteldrehung nach rechts
                            target = self.rabot.calculate_target_angle("right", 90)
                            self.rabot.turn_Degree(30, "right", target)
                            print("Rabot macht eine Vierteldrehung nach rechts")

                case Zustand.RobiFährtVorwärtsLetzteReihe:
                    rabot.getDistSensorValues()
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] < 30 or frontSensors[1] < 30:
                        zustand = Zustand.RobiStoppt
                        print("Rabot stoppt")

                case Zustand.RobiStoppt:
                    self.rabot.stop()
                    ProgrammStatus = False

                case _:
                    print ("Ungültiger Zustand: " + str(zustand))

    def test_crawler(self, speed):
        self.rabot.enable_crawler()
        time.sleep(1)
        self.rabot.drive_straight(speed)
        self.rabot.read_rpm()
        time.sleep(1)
        self.rabot.read_rpm()
        time.sleep(4)
        self.rabot.stop_crawler()
        time.sleep(1)
        self.rabot.rotate_crawler(speed, "left")
        time.sleep(4)
        self.rabot.read_rpm()
        self.rabot.drive_straight(speed)
        time.sleep(4)
        self.rabot.rotate_crawler(speed, "right")
        self.rabot.read_rpm()
        time.sleep(3)
        #self.rabot.turn_crawler(speed, 50)
        #time.sleep(3)
        #self.rabot.turn_crawler(speed, -50)
        #time.sleep(3)
        self.rabot.stop_crawler()
        time.sleep(1)
        self.rabot.disable_crawler()

    def test_ablauf(self, speed):
        self.rabot.enable_crawler()
        time.sleep(1)
        for i in range(2):
            self.rabot.drive_straight(speed)
            time.sleep(6)
            #self.rabot.stop_crawler()
            #time.sleep(0.1)
            self.rabot.rotate_crawler((speed-250), "left")
            time.sleep(3)
            self.rabot.drive_straight(speed)
            time.sleep(1.5)
            self.rabot.rotate_crawler((speed-250), "left")
            time.sleep(3)
            self.rabot.drive_straight(speed)
            time.sleep(6)
            #self.rabot.stop_crawler()
            #time.sleep(0.1)
            self.rabot.rotate_crawler((speed-250), "right")
            time.sleep(3)
            self.rabot.drive_straight(speed)
            time.sleep(1.5)
            self.rabot.rotate_crawler((speed-250), "right")
            time.sleep(3)
        self.rabot.drive_straight(speed)
        time.sleep(6)
        self.rabot.stop_crawler()
        time.sleep(1)
        self.rabot.disable_crawler()

if __name__ == '__main__':
    rabot = Rabot()
    # rabot.test()
    # rabot.drivestraight(-50)
    rabot.alignApwards()
    # rabot.rotate(50, "right", 90)
    #rabot.test_crawler(750)
    #rabot.test_ablauf(750)
    #rabot.test_turn(500)