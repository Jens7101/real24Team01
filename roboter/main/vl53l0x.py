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
    address = 0x10  # Neue Startadresse für die Sensoren
    Hubs_mit_Sensordaten = []

    bus = smbus.SMBus(i2c_bus_number)  # I2C-Bus öffnen
    print(Hubs)

    for Hub in Hubs:
        PA_HUB_I2C_ADDRESS = Hub[0]
        sensors = []
        PA_HUB_I2C_ADDRESS_mit_sensors = []
        for channel in Hub[1]:
            select_mux_channel(bus, channel, PA_HUB_I2C_ADDRESS)  # Wähle den entsprechenden Kanal

            tof = VL53L0X.VL53L0X(0x29)  # Standardadresse des Sensors
            tof.device_address = address  # Sensor auf neue Adresse setzen
            
            address += 2  # Nächste Adresse für den nächsten Sensor

            tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
            sensors.append(tof)
        PA_HUB_I2C_ADDRESS_mit_sensors.extend([PA_HUB_I2C_ADDRESS, sensors])
        Hubs_mit_Sensordaten.append(PA_HUB_I2C_ADDRESS_mit_sensors)
        
    print (Hubs_mit_Sensordaten) 
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
    bus.write_byte(PA_HUB_I2C_ADDRESS, 1 << channel)
    time.sleep(0.02)  # Kleine Verzögerung nach Kanalwechsel