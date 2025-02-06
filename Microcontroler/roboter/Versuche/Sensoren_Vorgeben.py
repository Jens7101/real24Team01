from driver.vl53l0x_helper import init_vl53l0x
import flink

# Definiere die GPIOs direkt im Code (anstatt über Argumente)
gpios = [0, 1]  # Beispiel: Sensoren an GPIO 0, 1 und 2
# other_pins = [3, 4]  # Falls nötig, GPIOs zum Deaktivieren anderer Sensoren

# Initialisiere die ToF-Sensoren
# tofs = init_vl53l0x(gpios)
tofs = init_vl53l0x([0, 1])


# Messwerte ausgeben
for _ in range(1, 9999999):
    line = " ".join(["% d" % tof.get_distance() for tof in tofs])
    print("distance %s" % line)
