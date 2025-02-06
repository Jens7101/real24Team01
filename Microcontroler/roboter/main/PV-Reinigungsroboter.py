from driver.vl53l0x_helper import init_vl53l0x
import flink
import time


class Robi:    
    
    def Reinigen (self, maxWandberuehrungen):
        """
        Der Roboter Fährt an den Oberen Rand des Pannels.
        dan fährt zur Linken obereb Ecke.
        Anschliessend reinigt er das Panel von Oben nach unten.
        """

        Zustand = Enum ('Zustand', ['RobiDrehenBisHorizontal', 'RobiFaehrtVorärts1', 'RobiViertelDrehungLinks', 'RobiFaertVorwärts2', 'RobiDreht180', 
        'ViertelDrehungRechts_Zy' , 'ViertelDrehungLinks_Zy', 'RobiFaertVorwärts3', 'RobiFaertRunter'])
        
        print ("PANEL REINIGEN")

        # Initialisiere die ToF-Sensoren
        tofs = init_vl53l0x([0, 1])
        
        # Gyrosensor Auslesen
        winkel = sensor auslesen

        if winkel > 180: # Rechts drehen
            rechtsdrehen
        else: # Links drehen
        

        
        anzahlWandberuehrungen = 0
        uhr = Sanduhr ()
        zustand = Zustand.RobiFaehrtVorwaerts

        self.robi.connect ()
        self.robi.drive (5)
        print ("Robi faehrt vorwaerts")

        while anzahlWandberuehrungen < maxWandberuehrungen:
            time.sleep(1 / 1000)
            match zustand:
                
                case Zustand.RobiDrehenBisHorizontal:
                    '''self.robi.getDistSensorValues ()
                    if self.anWand ():
                        self.bodenSensorWerteAusgeben ()
                        self.robi.drive (-10)
                        uhr.starten (1000)
                        zustand = Zustand.RobiFaehrtRueckwaerts
                        print ("Robi faehrt rueckwaerts")'''

                case Zustand.RobiFaehrtVorärts1:
                   ''' if uhr.abgelaufen():
                        self.robi.turn (20)
                        uhr.starten (2000)
                        zustand = Zustand.RobiDrehtAb
                        print ("Robi dreht ab")'''

                case Zustand.RobiViertelDrehungLinks:
                    '''if uhr.abgelaufen ():
                        anzahlWandberuehrungen += 1
                        self.robi.drive (5)
                        zustand = Zustand.RobiFaehrtVorwaerts
                        print ("Robi faehrt vorwaerts")'''

                case Zustand.RobiFaertVorwärts2:

                #case Zustand.RobiDreht180:

                #case Zustand.ViertelDrehungRechts_Zy:

                #case Zustand.ViertelDrehungLinks_Zy:

                #case Zustand.RobiFaertVorwärts3:

                #case Zustand.RobiFahertRunter:

                #case _:
                    print ("Ungültiger Zustand: " + str(zustand))

        self.robi.stop ()
        self.robi.disconnect ()
        print ("FERTIG")


if __name__ == '__main__':
    robi = Robi ("localhost", 3000)