from driver.vl53l0x_helper import init_vl53l0x
import flink

__author__ = "Moritz Lammerich"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

# Definiere die GPIOs direkt im Code (anstatt über Argumente)
gpios = [0]  # Beispiel: Sensoren an GPIO 0, 1 und 2
# other_pins = [3, 4]  # Falls nötig, GPIOs zum Deaktivieren anderer Sensoren

# Set 'other' GPIOS low, um nicht getestete Sensoren zu deaktivieren
'''gpio = flink.FlinkGPIO()
for pin in other_pins:
    gpio.setDir(pin, True)
    gpio.setValue(pin, False)'''

# Initialisiere die ToF-Sensoren
tofs = init_vl53l0x(gpios)

'''# Benutzer wählen lassen, welcher Sensor ausgegeben werden soll
print(f"Verfügbare Sensoren: {gpios}")
sensor_index = input("Welchen Sensor möchtest du ausgeben? (Index eingeben, oder leer lassen für alle): ")

if sensor_index.isdigit():
    sensor_index = int(sensor_index)
    if 0 <= sensor_index < len(tofs):
        selected_tofs = [tofs[sensor_index]]
    else:
        print("Ungültige Eingabe. Zeige alle Sensoren an.")
        selected_tofs = tofs
else:
    selected_tofs = tofs'''

# Messwerte ausgeben
for _ in range(1, 11):
    line = " ".join(["% d" % tof.get_distance() for tof in tofs])
    print("distance %s" % line)
