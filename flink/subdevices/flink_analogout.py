import flink
import ctypes as ct

__author__ = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkAnalogOut(flink.FlinkSubDevice):
    """
    The flink AnalogOut subdevice realizes analog outputs in a flink device.
    Its number of channels depends on the actual dac chip used.
    """
    AD5668 = 1 

    def __init__(self, subType: int):
        """
        Creates a DAC converter object.
        
        Parameters
        ----------
        subType : subtype, e.g. AD5668

        Returns
        -------
        the object
        """
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.ANALOG_OUTPUT_INTERFACE_ID, subType)
        super().__init__(dev, subDev)
        dev.lib.flink_analog_out_get_resolution.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_analog_out_get_resolution.restype = ct.c_int
        dev.lib.flink_analog_out_set_value.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_analog_out_set_value.restype = ct.c_int

    def getResolution(self) -> int:
        """
        Reads the resolution field of the subdevice. The field denotes the number of 
        resolvable steps, e.g. a 12 bit converter delivers 4096 steps.
        
        Returns
        -------
        number of resolvable steps
        """
        res = ct.c_uint32()
        error = self.dev.lib.flink_analog_out_get_resolution(self.subDev, ct.byref(res))
        if error < 0:
            raise flink.FlinkException("Failed to get resolution from dac subdevice", error, self.subDev)
        return res.value

    def setValue(self, channel: int, value: int) -> None:
        """
        Sets the digital value for a channel. 
        Channel number must be 0 < channel < nof available channels.
        
        Parameters
        ----------
        channel : channel number 
        value : digital value
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_analog_out_set_value(self.subDev, channel, ct.byref(val))
        if error < 0:
            raise flink.FlinkException("Failed to set value on dac subdevice", error, self.subDev)
            