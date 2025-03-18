import importlib
from vl53l0x import init_vl53l0xx
from vl53l0x import select_mux_channel
import smbus

'''


'''

'''XSHUT über die GPIO's deaktivieren und wieder aktivieren, damit die initialiseirung neu funktioniert.'''


gpio = flink.FlinkGPIO()
for pin in :
    gpio.setDir(pin, True)
    gpio.setValue(pin, False)

# I2C-Busnummer (je nach Board kann das 0 oder 1 sein, bitte mit `i2cdetect -l` prüfen)
I2C_BUS = 0

# Liste der Multiplexer-Kanäle, an denen die VL53L0X-Sensoren angeschlossen sind
MUX_CHANNELS = [0, 1]  # Beispiel: Sensoren an Kanal 0 und 1 des PA.Hub

# Initialisiere die ToF-Sensoren über den PA.Hub
tofs = init_vl53l0xx(I2C_BUS, MUX_CHANNELS)

'''New Code'''
bus = smbus.SMBus(I2C_BUS)  # I2C-Bus öffnen

# Messwerte ausgeben
index = 1
while True:

    line = ""

    for tof in tofs:
        
        line += ("%d" % tof.get_distance())
        
        select_mux_channel(bus, MUX_CHANNELS[index])
        index = (index + 1) % len(MUX_CHANNELS)
    
    print("distance %s" % line)
    

for tof in tofs:
    tof.stop_ranging()

