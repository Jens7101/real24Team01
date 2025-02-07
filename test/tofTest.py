import argparse

from driver.vl53l0x_helper import init_vl53l0x
import flink

__author__ = "Moritz Lammerich"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"


# set up and parse command line arguments
parser = argparse.ArgumentParser(
    prog='tof-test',  description='Test utility for VL53L0x ToF sensors')
parser.add_argument('-g', '--gpios', nargs='+',
                    type=int, dest='gpios',
                    metavar='PIN',
                    required=True,
                    help='Flink GPIO channels to which the sensors\' \
                    XSHUT pin is connected, the number of sensors is inferred\
                    from the number of GPIO channels')
parser.add_argument('-o', '--other', nargs='+',
                    type=int, dest='other_pins',
                    metavar='PIN',
                    help='GPIO channels of sensors that are connected but not\
                    under test. These will be set low to disable those sensors\
                    so they don\'t interfere with the sensors under test.\
                    GPIOs specified in -g -o will work the same as if only\
                    specified in -g (i.e -o has no ill effect)')

args = parser.parse_args()

# set 'other' GPIOS low, so that sensors that aren't tested can be disabled
gpio = flink.FlinkGPIO()
for pin in args.other_pins:
    gpio.setDir(pin, True)
    gpio.setValue(pin, False)


# initialize the ToF sensors
tofs = init_vl53l0x(args.gpios)

# print measurements
for _ in range(1, 11):
    line = " ".join(["% d" % tof.get_distance() for tof in tofs])
    print("distance %s" % line)
