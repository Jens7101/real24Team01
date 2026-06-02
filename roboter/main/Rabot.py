"""
Rabot control script
--------------------
Hauptprogramm für den Roboter: enthält die Klasse `Rabot` mit einfachen
Zustandsautomaten (für Demo-Fahrt), Sensor-Threads und Steuerungsroutinen.
"""

from doctest import debug
from enum import Enum
from RabotAPI import *
from Sanduhr import *
import random
import flink
import time
from threading import Timer
import threading
import queue

class Rabot:

    def __init__(self):

        '''Erzeuge Rabot-Hilfsobjekte.

        `RabotAPI` kapselt Hardwarezugriff; hier werden Standardparameter gesetzt
        und die interne Queue für Ereignisse (z. B. Hindernisse) angelegt.
        '''
        self.rabot = RabotAPI()
        self.q = queue.Queue()
        # Parameter setzen
        self.DistanzSolarpanel = 150
        self.tol_angel = 5

    def Timer_abgelaufen(self):
        self.timer_abgelaufen = True

    
    def Thread_read_sensors(self):
        # Hintergrund-Thread: liest in konstanter Frequenz alle Sensorwerte aus
        while self.ProgrammStatus:
            self.rabot.getsensorValues()
            debug = False
            if debug:
                print("Sensorwerte: " + str(self.rabot.sensorwerte))
                print("Pitch: " + str(self.rabot.pitch) + " Roll: " + str(self.rabot.roll))
            # 50 Hz Messfrequenz (20 ms)
            time.sleep(0.02)


    def Thread_detect_obstacle(self):
        hindernis_aktiv = False
        print ("Hinderniserkennung gestartet")

        # Hintergrund-Thread: prüft schnell nur die relevanten Front-Sensoren und
        # signalisiert ein Event in der Queue, wenn ein Hindernis erkannt wurde.
        while self.ProgrammStatus:
            frontSensors = self.rabot.sensorwerte[4:6] # Sensoren für Hinderniserkennung
            debug = False
            if debug:
                print("Front Sensorwerte: " + str(frontSensors))
            if (frontSensors[0] < self.DistanzSolarpanel or frontSensors[1] < self.DistanzSolarpanel) and not hindernis_aktiv:
                hindernis_aktiv = True
                # Thread meldet: Hindernis erkannt
                self.q.put("obstacle_detected")
            elif (frontSensors[0] >= self.DistanzSolarpanel and frontSensors[1] >= self.DistanzSolarpanel) and hindernis_aktiv:
                hindernis_aktiv = False
            # Sehr schnell prüfen (hier 1 ms); bei Bedarf erhöhen, um CPU-Last zu reduzieren
            time.sleep(1 / 1000)


    def first_demo_programm_Motor(self):
        # Definiere Zustände des einfachen Zustandsautomaten (für Demonstrationsfahrt)
        Zustand = Enum ('Zustand', ['RobiDrehtBisHorizontal', 'RobiFährVorwärts1',
            'RobiAusrichten', 'RobiVierteldrehungLinks1', 'RobiFährtVorwärts2',
            'RobiDreht180', 'ViertelDrehungRechts_Zy', 'RobiFährtRunter_Zy',
            'ViertelDrehungLinks_Zy', 'RobiFährtVorwärts_Zy', 'RobiStoppt',
            "RobiFährtVorwärtsLetzteReihe", "HindernisErkannt"] )

        self.ProgrammStatus = True

        # Starte Thread zum regelmäßigen Auslesen aller Sensoren
        read_sensors_thread = threading.Thread(target=self.Thread_read_sensors)
        read_sensors_thread.start()

        # Kurz warten, damit erste Sensorwerte vorliegen
        time.sleep(5)

        # Starte Thread für Hinderniserkennung (setzt Events in self.q)
        obstacle_thread = threading.Thread(target=self.Thread_detect_obstacle)
        obstacle_thread.start()



        
        self.rabot.getPitchRoll()
        zustand = Zustand.RobiDrehtBisHorizontal
        rpm = 500
        self.rabot.startup_crawlers()
        self.drive_back_time = 1.5
        
        '''for i in range(10):
            self.rabot.getPitchRoll()
            time.sleep(0.1)'''
      

        if self.rabot.pitch >= 0:
            self.rabot.crawler_turn_left(rpm)
            print("Rabot dreht links")
            print(self.rabot.pitch)
        elif self.rabot.pitch < 0:
            self.rabot.crawler_turn_right(rpm)
            print("Rabot dreht rechts")
            print(self.rabot.pitch)

        

        while self.ProgrammStatus:
            time.sleep(1 / 1000) # Frequenz in der die Zustände abgefragt werden

            # abfrage Hindernis Erkennung in eigenem Thread
            try:
                state = self.q.get(timeout=1)
                if state == "obstacle_detected":
                    previesZustand = zustand # vorherigen Zustand speichern, um nach der Hindernisbewältigung fortzufahren
                    zustand = Zustand.HindernisErkannt

            except queue.Empty:
                pass

            match zustand:
                case Zustand.RobiDrehtBisHorizontal:
                    self.rabot.getPitchRoll()
                    debug = True
                    if debug:
                        print ("Pitch: " + str(self.rabot.pitch) + " Roll: " + str(self.rabot.roll))
                    if abs(self.rabot.pitch) < 1:
                        zustand = Zustand.RobiFährVorwärts1
                        self.rabot.crawler_drive(rpm)
                        print("Rabot fährt vorwärts")

                case Zustand.RobiFährVorwärts1:
                    frontSensors = self.rabot.sensorwerte[0:2]

                    if frontSensors[0] > self.DistanzSolarpanel:
                        self.rabot.crawler_stop()
                        zustand = Zustand.RobiAusrichten
                        self.rabot.crawler_drive_seperat(0, rpm)
                        print("Rabot richtet sich aus") 
                    elif frontSensors[1] > self.DistanzSolarpanel:
                        self.rabot.crawler_stop()
                        zustand = Zustand.RobiAusrichten
                        self.rabot.crawler_drive_seperat(rpm, 0)
                        print("Rabot richtet sich aus")  

                case Zustand.RobiAusrichten:
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] > self.DistanzSolarpanel and frontSensors[1] > self.DistanzSolarpanel:
                        zustand = Zustand.RobiVierteldrehungLinks1
                        self.rabot.crawler_stop()
                        self.rabot.crawler_drive(-rpm)
                        time.sleep(self.drive_back_time)
                        self.rabot.calculate_target_angle("left", 90)
                        self.rabot.crawler_turn_left(rpm)
                        print("Rabot macht eine Vierteldrehung nach links")

                case Zustand.RobiVierteldrehungLinks1:
                    if debug:
                        print("Aktueller Yaw: " + str(self.rabot._yaw))
                        print("Ziel Yaw: " + str(self.rabot.targetAngle))
                    if self.rabot.targetAngle - self.tol_angel < self.rabot._yaw < self.rabot.targetAngle + self.tol_angel:
                        zustand = Zustand.RobiFährtVorwärts2
                        self.rabot.crawler_drive(rpm)
                        Vorwärts = 1
                        print("Rabot fährt vorwärts")

                case Zustand.RobiFährtVorwärts2:
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] > self.DistanzSolarpanel or frontSensors[1] > self.DistanzSolarpanel:
                        self.rabot.crawler_stop()

                        if Vorwärts == 2:
                            zustand = Zustand.ViertelDrehungRechts_Zy
                            # Parameter für Zyklus
                            Drehen = 1
                            rechtsLinks = "right"
                            lastRow = False
                            # Rabot macht eine Vierteldrehung nach rechts
                            self.rabot.crawler_drive(-rpm)
                            time.sleep(self.drive_back_time)
                            self.rabot.calculate_target_angle("right", 90)
                            self.rabot.crawler_turn_right(rpm)
                            print("Rabot macht eine Vierteldrehung nach rechts")

                        elif Vorwärts == 1:
                            zustand = Zustand.RobiDreht180
                            # Parameter für 180 Grad Drehung
                            Vorwärts = 2
                            # Rabot dreht sich um 180 Grad
                            self.rabot.crawler_drive(-rpm)
                            time.sleep(self.drive_back_time)
                            self.rabot.calculate_target_angle("left", 180)
                            self.rabot.crawler_turn_left(rpm)
                            print("Rabot dreht sich um 180 Grad")

                case Zustand.RobiDreht180:
                    if debug:
                        print("Aktueller Yaw: " + str(self.rabot._yaw))
                        print("Ziel Yaw: " + str(self.rabot.targetAngle))
                    if self.rabot.targetAngle - self.tol_angel < self.rabot._yaw < self.rabot.targetAngle + self.tol_angel:
                        zustand = Zustand.RobiFährtVorwärts2
                        self.rabot.crawler_drive(rpm)
                        print("Rabot hat sich um 180 Grad gedreht")
                        self.rabot.startup_brushes()

                case Zustand.ViertelDrehungRechts_Zy:
                    debug = True
                    if debug:
                        print("Aktueller Yaw: " + str(self.rabot._yaw))
                        print("Ziel Yaw: " + str(self.rabot.targetAngle))
                    if self.rabot.targetAngle - self.tol_angel < self.rabot._yaw < self.rabot.targetAngle + self.tol_angel:
                        print(Drehen)
                        if Drehen == 1:
                            zustand = Zustand.RobiFährtRunter_Zy
                            self.timer_abgelaufen = False
                            timer = Timer(2.0, self.Timer_abgelaufen)
                            timer.start()
                            self.rabot.crawler_drive(rpm)
                            print("Rabot fährt runter")
                        elif Drehen == 2:
                            if lastRow == True:
                                zustand = Zustand.RobiFährtVorwärtsLetzteReihe
                                self.rabot.crawler_drive(rpm)
                                print("Rabot fährt die letzte Reihe vorwärts")
                            else:
                                zustand = Zustand.RobiFährtVorwärts_Zy
                                # Parameter für Zyklus
                                rechtsLinks = "left"
                                # Rabot fährt geradeaus
                                self.rabot.crawler_drive(rpm)
                                print("Rabot fährt geradeaus")



                case Zustand.RobiFährtRunter_Zy:
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] > self.DistanzSolarpanel or frontSensors[1] > self.DistanzSolarpanel:
                        timer.cancel()
                        if rechtsLinks == "left":
                            self.rabot.crawler_stop()
                            zustand = Zustand.ViertelDrehungLinks_Zy
                            # Parameter für Zyklus
                            lastRow = True
                            Drehen = 2
                            self.rabot.crawler_drive(-rpm)
                            time.sleep(self.drive_back_time+ 3)
                            self.rabot.calculate_target_angle("left", 90)
                            self.rabot.crawler_turn_left(rpm)
                            print("Rabot macht eine Vierteldrehung nach links")
                            print("last row")
                        elif rechtsLinks == "right":
                            self.rabot.crawler_stop()
                            zustand = zustand.ViertelDrehungRechts_Zy
                            # Parameter für Zyklus
                            lastRow = True
                            Drehen = 2
                            self.rabot.calculate_target_angle("right", 90)
                            self.rabot.crawler_turn_right(rpm)
                            print("Rabot macht eine Vierteldrehung nach rechts")
                            print("last row")

                    elif self.timer_abgelaufen == True:
                        if rechtsLinks == "left":
                            zustand = Zustand.ViertelDrehungLinks_Zy
                            Drehen = 2
                            self.rabot.calculate_target_angle("left", 90)
                            self.rabot.crawler_turn_left(rpm)
                            print("Rabot macht eine Vierteldrehung nach links")

                        elif rechtsLinks == "right":
                            zustand = Zustand.ViertelDrehungRechts_Zy
                            Drehen = 2
                            self.rabot.calculate_target_angle("right", 90)
                            self.rabot.crawler_turn_right(rpm)
                            print("Rabot macht eine Vierteldrehung nach rechts") 

                case Zustand.ViertelDrehungLinks_Zy:
                    if debug:
                        print("Aktueller Yaw: " + str(self.rabot._yaw))
                        print("Ziel Yaw: " + str(self.rabot.targetAngle))
                    if self.rabot.targetAngle - self.tol_angel < self.rabot._yaw < self.rabot.targetAngle + self.tol_angel:
                        print(Drehen)
                        if Drehen == 1:
                            zustand = Zustand.RobiFährtRunter_Zy
                            self.timer_abgelaufen = False
                            timer = Timer(2.0, self.Timer_abgelaufen)
                            timer.start()
                            self.rabot.crawler_drive(rpm)
                            print("Rabot fährt runter")
                        elif Drehen == 2:
                            if lastRow == True:
                                zustand = Zustand.RobiFährtVorwärtsLetzteReihe
                                self.rabot.crawler_drive(rpm)
                                print("Rabot fährt die letzte Reihe vorwärts")
                            else:
                                zustand = Zustand.RobiFährtVorwärts_Zy
                                # Parameter für Zyklus
                                rechtsLinks = "right"
                                # Rabot fährt geradeaus
                                self.rabot.crawler_drive(rpm)
                                print("Rabot fährt geradeaus")

                case Zustand.RobiFährtVorwärts_Zy:
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] > self.DistanzSolarpanel or frontSensors[1] > self.DistanzSolarpanel:
                        self.rabot.crawler_stop()

                        if rechtsLinks == "left":
                            zustand = Zustand.ViertelDrehungLinks_Zy
                            # Parameter für Zyklus
                            Drehen = 1
                            # Rabot macht eine Vierteldrehung nach links
                            self.rabot.crawler_drive(-rpm)
                            time.sleep(self.drive_back_time)
                            self.rabot.calculate_target_angle("left", 90)
                            self.rabot.crawler_turn_left(rpm)
                            print("Rabot macht eine Vierteldrehung nach links")
                        elif rechtsLinks == "right":
                            zustand = Zustand.ViertelDrehungRechts_Zy
                            # Parameter für Zyklus
                            Drehen = 1
                            # Rabot macht eine Vierteldrehung nach rechts
                            self.rabot.crawler_drive(-rpm)
                            time.sleep(self.drive_back_time)
                            self.rabot.calculate_target_angle("right", 90)
                            self.rabot.crawler_turn_right(rpm)
                            print("Rabot macht eine Vierteldrehung nach rechts")

                case Zustand.RobiFährtVorwärtsLetzteReihe:
                    frontSensors = self.rabot.sensorwerte[0:2]
                    if frontSensors[0] > self.DistanzSolarpanel or frontSensors[1] > self.DistanzSolarpanel:
                        zustand = Zustand.RobiStoppt
                        print("Rabot stoppt")

                case Zustand.HindernisErkannt:
                    zustand = Zustand.RobiStoppt
                    self.rabot.crawler_stop()
                    print("Hindernis erkannt, Rabot stoppt")

                case Zustand.RobiStoppt:
                    self.rabot.close_crawlers()
                    self.rabot.close_brushes()
                    self.ProgrammStatus = False
                    obstacle_thread.join()
                    print("Programm beendet")

                case _:
                    print ("Ungültiger Zustand: " + str(zustand))           
    
    
    def Rabot_test(self):
        self.rabot.update_crawler_acc_dcc(5000,5000)
        self.rabot.startup_crawlers()
        self.rabot.crawler_drive(500)
        time.sleep(2)
        self.rabot.crawler_stop()
        self.rabot.close_crawlers()


if __name__ == '__main__':
    rabot = Rabot()
    # rabot.test()
    # rabot.drivestraight(50)
    # rabot.alignApwards()
    # rabot.rotate(50, "right", 90)
    # rabot.first_demo_programm()
    rabot.first_demo_programm_Motor()
    # rabot.Rabot_test()
    # rabot.alignApwards_eigene_Lagemessung()
