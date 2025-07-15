import importlib
from vl53l0x import init_vl53l0xx
from vl53l0x import select_mux_channel
import smbus
import flink
import time

class Distance_Sensors:

    def __init__(self):
        # I2C-Busnummer (je nach Board kann das 0 oder 1 sein, bitte mit `i2cdetect -l` prüfen)
        self.I2C_BUS = 0

        # Liste der Multiplexer-Kanäle, an denen die VL53L0X-Sensoren angeschlossen sind
        self.MUX_CHANNELS = [0, 1]  # Beispiel: Sensoren an Kanal 0 und 1 des PA.Hub

        # XSHUT über die GPIO's deaktivieren und wieder aktivieren, damit die initialiseirung neu funktioniert.
        gpio = flink.FlinkGPIO()
        for pin in self.MUX_CHANNELS:
            gpio.setDir(pin, True)
            gpio.setValue(pin, False)
            time.sleep(0.01)
            gpio.setValue(pin, True)

        # Initialisiere die ToF-Sensoren über den PA.Hub
        self.tofs = init_vl53l0xx(self.I2C_BUS, self.MUX_CHANNELS)
        self.sensorwerte = [0] * 20

    def getDistanceSensors(self):
        bus = smbus.SMBus(self.I2C_BUS)  # I2C-Bus öffnen
        index = 0
        # Messwerte ausgeben
        for tof in self.tofs:
            select_mux_channel(bus, self.MUX_CHANNELS[index])
            self.sensorwerte[index] = tof.get_distance()
            index += 1

    
