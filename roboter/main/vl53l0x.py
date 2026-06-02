"""
vl53l0x helper
----------------
Hilfsfunktionen zur Initialisierung mehrerer VL53L0X Time-of-Flight Sensoren
über einen PA.Hub I2C-Multiplexer. Diese Datei kapselt Kanalwahl und Adressvergabe.
"""

import flink
import time
import VL53L0X
import smbus

__author__ = "Moritz Lammerich"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

def init_vl53l0xx(i2c_bus_number, Hubs):
    """
    Initialisiert mehrere VL53L0X-Sensoren über den PA.Hub Multiplexer.

    Parameters:
    -----------
    i2c_bus_number: int
        Nummer des I2C-Busses, an dem der PA.Hub angeschlossen ist.
    mux_channels: list
        Liste mit den Multiplexer-Kanälen (0-7), an denen die Sensoren hängen.

    Returns:
    --------
    List of initialized sensors.
    """
    # Startadresse für umadressierte VL53L0X Sensoren (muss mit dem Treiber kompatibel sein)
    address = 0x10
    Hubs_mit_Sensordaten = []

    # I2C-Bus öffnen (wird vom Aufrufer in RabotAPI als smbus.SMBus gehalten)
    bus = smbus.SMBus(i2c_bus_number)

    for Hub in Hubs:
        PA_HUB_I2C_ADDRESS = Hub[0]
        sensors = []
        PA_HUB_I2C_ADDRESS_mit_sensors = []
        for channel in Hub[1]:
            # Wähle den jeweiligen Multiplexer-Kanal, damit der physische Sensor an 0x29
            # angesprochen werden kann und anschließend eine neue Adresse zugewiesen wird.
            select_mux_channel(bus, channel, PA_HUB_I2C_ADDRESS)

            # Erzeuge ein VL53L0X-Objekt mit Standardadresse (0x29)
            tof = VL53L0X.VL53L0X(0x29)
            # Weise dem Sensor eine neue, eindeutige Adresse zu
            tof.device_address = address
            address += 2  # erhöhe die Adresse für den nächsten Sensor

            # Starte Messung mit besserer Genauigkeit
            tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
            sensors.append(tof)

        # Sammle Hub-Adresse und die zugehörigen Sensorobjekte
        PA_HUB_I2C_ADDRESS_mit_sensors.extend([PA_HUB_I2C_ADDRESS, sensors])
        Hubs_mit_Sensordaten.append(PA_HUB_I2C_ADDRESS_mit_sensors)

        # Deaktiviere alle Kanäle am Hub nach der Initialisierung, um Buskollisionen zu vermeiden
        bus.write_byte(PA_HUB_I2C_ADDRESS, 0x00)

    return Hubs_mit_Sensordaten

def select_mux_channel(bus, channel, PA_HUB_I2C_ADDRESS):
    """
    Wählt den entsprechenden Kanal des PA.Hub Multiplexers aus.

    Parameters:
    -----------
    bus: smbus.SMBus instance
        Der I2C-Bus, an dem der Multiplexer angeschlossen ist.
    channel: int
        Der Multiplexer-Kanal (0-7), auf dem der gewünschte Sensor liegt.
    """
    # Schreibe das Bitmuster (1<<channel) in den Hub, um nur den gewünschten Kanal zu aktivieren
    bus.write_byte(PA_HUB_I2C_ADDRESS, 1 << channel)
    # Sehr kurze Verzögerung, damit sich der Multiplexer und der Sensor stabilisieren
    time.sleep(0.0005)