class Robi:    
    
    def Reinigen (self, maxWandberuehrungen):
        """
        Der Roboter Fährt an den Oberen Rand des Pannels.
        dan fährt zur Linken obereb Ecke.
        Anschliessend reinigt er das Panel von Oben nach unten.
        """

        Zustand = Enum ('Zustand', ['RobiFaehrtVorwaerts', 'RobiFaehrtRueckwaerts', 'RobiDrehtAb'])

        print ("PLANLOS FAHREN")
        anzahlWandberuehrungen = 0
        uhr = Sanduhr ()
        zustand = Zustand.RobiFaehrtVorwaerts

        self.robi.connect ()
        self.robi.drive (5)
        print ("Robi faehrt vorwaerts")

        while anzahlWandberuehrungen < maxWandberuehrungen:
            time.sleep(1 / 1000)
            match zustand:
                
                case Zustand.RobiFaehrtVorwaerts:
                    self.robi.getDistSensorValues ()
                    if self.anWand ():
                        self.bodenSensorWerteAusgeben ()
                        self.robi.drive (-10)
                        uhr.starten (1000)
                        zustand = Zustand.RobiFaehrtRueckwaerts
                        print ("Robi faehrt rueckwaerts")

                case Zustand.RobiFaehrtRueckwaerts:
                    if uhr.abgelaufen():
                        self.robi.turn (20)
                        uhr.starten (2000)
                        zustand = Zustand.RobiDrehtAb
                        print ("Robi dreht ab")

                case Zustand.RobiDrehtAb:
                    if uhr.abgelaufen ():
                        anzahlWandberuehrungen += 1
                        self.robi.drive (5)
                        zustand = Zustand.RobiFaehrtVorwaerts
                        print ("Robi faehrt vorwaerts")

                case _:
                    print ("Ungültiger Zustand: " + str(zustand))

        self.robi.stop ()
        self.robi.disconnect ()
        print ("FERTIG")


if __name__ == '__main__':
    robi = Robi ("localhost", 3000)