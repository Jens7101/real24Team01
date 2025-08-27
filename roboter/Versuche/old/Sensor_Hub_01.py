import importlib
from vl53l0x import init_vl53l0xx

'''
Mit diesem Programm wird nur der Zuletst geöffnete Sensor ausgelesen
'''

init = True

if init == True:
    # I2C-Busnummer (je nach Board kann das 0 oder 1 sein, bitte mit `i2cdetect -l` prüfen)
    I2C_BUS = 0

    # Liste der Multiplexer-Kanäle, an denen die VL53L0X-Sensoren angeschlossen sind
    MUX_CHANNELS = [0, 1]  # Beispiel: Sensoren an Kanal 0 und 1 des PA.Hub

    # Initialisiere die ToF-Sensoren über den PA.Hub
    tofs = init_vl53l0xx(I2C_BUS, MUX_CHANNELS)

# Messwerte ausgeben
for i in range(15):
    line = " ".join(["%d" % tof.get_distance() for tof in tofs])
    print("distance %s" % line)

for tof in tofs:
    tof.stop_ranging()
