import flink
import time
import VL53L0X
import smbus

__author__ = "Moritz Lammerich"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

# I2C-Adresse des PA.Hub (TCA9548A Multiplexer)
PA_HUB_I2C_ADDRESS = 0x70

def select_mux_channel(bus, channel):
    """
    Wählt den entsprechenden Kanal des PA.Hub Multiplexers aus.

    Parameters:
    -----------
    bus: smbus.SMBus instance
        Der I2C-Bus, an dem der Multiplexer angeschlossen ist.
    channel: int
        Der Multiplexer-Kanal (0-7), auf dem der gewünschte Sensor liegt.
    """
    bus.write_byte(PA_HUB_I2C_ADDRESS, 1 << channel)
    time.sleep(0.01)  # Kleine Verzögerung nach Kanalwechsel

def init_vl53l0xx(i2c_bus_number, mux_channels):
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
    address = 0x10  # Neue Startadresse für die Sensoren
    sensors = []

    bus = smbus.SMBus(i2c_bus_number)  # I2C-Bus öffnen

    for channel in mux_channels:
        select_mux_channel(bus, channel)  # Wähle den entsprechenden Kanal

        tof = VL53L0X.VL53L0X(0x29)  # Standardadresse des Sensors
        tof.change_address(address)  # Sensor auf neue Adresse setzen
        address += 2  # Nächste Adresse für den nächsten Sensor

        tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
        sensors.append(tof)

    return sensors
