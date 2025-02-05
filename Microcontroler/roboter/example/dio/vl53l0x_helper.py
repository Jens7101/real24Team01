import flink
import time
import VL53L0X


__author__ = "Moritz Lammerich"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"


def init_vl53l0x(shutdown_gpio_channels):
    """
    Initialize VL53L0X time of flight distance sensors.

    Parameters:
    -----------
    shutdown_gpio_channels: List GPIO channel numbers to which the XSHUT pin of
    the sensors is connected. The number of sensors is inferred from the number
    of elements in the list.

    Returns:
    --------
    List of initialized sensors. Call `read_distance()` on an element to read
    the distance measurement from that sensor.

    Example:
    ---------
    sensors = init_vl53l0x([0,1,2])
    for sensor in sensors:
        print(sensor.read_distance())
    """
    address = 0x10
    sensors = []

    gpio = flink.FlinkGPIO()

    for xshut in shutdown_gpio_channels:
        gpio.setDir(xshut, True)
        gpio.setValue(xshut, False)

    time.sleep(0.1)

    for xshut in shutdown_gpio_channels:

        tof = VL53L0X.VL53L0X(address)
        address += 2

        gpio.setValue(xshut, True)
        time.sleep(0.1)
        tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
        time.sleep(0.1)
        sensors.append(tof)

    return sensors
