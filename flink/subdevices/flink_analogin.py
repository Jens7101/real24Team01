import flink
import ctypes as ct

__author__ = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkAnalogIn(flink.FlinkSubDevice):
    """
    The flink AnalogIn subdevice realizes analog inputs in a flink device.
    Its number of channels depends on the actual adc chip used.
    """
    ADC128S102 = 1 
    AD7606 = 2
    AD7476 = 3

    def __init__(self, subType: int):
        """
        Creates a ADC converter object.
        
        Parameters
        ----------
        subType : subtype, e.g. ADC128S102, AD7606, AD7476

        Returns
        -------
        the object
        """
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.ANALOG_INPUT_INTERFACE_ID, subType)
        super().__init__(dev, subDev)
        dev.lib.flink_analog_in_get_resolution.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_analog_in_get_resolution.restype = ct.c_int
        dev.lib.flink_analog_in_get_value.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_analog_in_get_value.restype = ct.c_int

    def getResolution(self) -> int:
        """
        Reads the resolution field of the subdevice. The field denotes the number of 
        resolvable steps, e.g. a 12 bit converter delivers 4096 steps.
        
        Returns
        -------
        number of resolvable steps
        """
        res = ct.c_uint32()
        error = self.dev.lib.flink_analog_in_get_resolution(self.subDev, ct.byref(res))
        if error < 0:
            raise flink.FlinkException("Failed to get resolution from adc subdevice", error, self.subDev)
        return res.value

    def getValue(self, channel: int) -> int:
        """
        Reads the digital value of a channel. 
        Channel number must be 0 < channel < nof available channels.
        
        Parameters
        ----------
        channel : channel number 
        
        Returns
        -------
        digital value
        """
        val = ct.c_uint32()
        error = self.dev.lib.flink_analog_in_get_value(self.subDev, channel, ct.byref(val))
        if error < 0:
            raise flink.FlinkException("Failed to get value from adc subdevice", error, self.subDev)
        return val.value
            