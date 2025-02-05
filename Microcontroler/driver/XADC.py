import os

__author__  = "Michael Zimmerli"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class XADC:
    """
    Driver for XADC
    4 Channels Supported

    """
    def __init__(self):
        self.CH0_PATH = '/sys/bus/iio/devices/iio:device1/in_voltage8_raw'
        self.CH1_PATH = '/sys/bus/iio/devices/iio:device1/in_voltage9_raw'
        self.CH2_PATH = '/sys/bus/iio/devices/iio:device1/in_voltage10_raw'
        self.CH3_PATH = '/sys/bus/iio/devices/iio:device1/in_voltage11_raw'

    def read(self,channel):
        match channel:
            case 0:
                return self.__readFile(self.CH1_PATH)
            case 1:
                return self.__readFile(self.CH2_PATH)
            case 2:
                return self.__readFile(self.CH3_PATH)
            case 3:
                return self.__readFile(self.CH3_PATH)
            case _:
                return -1

    def __readFile(self,path):
        f = open(path)
        x = f.read().strip('\n')
        return int(x)
    
