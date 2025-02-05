import flink
import numpy
import ctypes as ct

__author__ = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkFQD(flink.FlinkSubDevice):
    """
    The flink FQD subdevice realizes fast quadrature decode function within a flink device.
    It offers several channels. Each channel uses a pin pair with signals A and B.
    """

    def __init__(self):
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.COUNTER_INTERFACE_ID)
        super().__init__(dev, subDev)
        dev.lib.flink_counter_set_mode.argtypes = [ct.c_void_p, ct.c_uint8]
        dev.lib.flink_counter_set_mode.restype = ct.c_int
        dev.lib.flink_counter_get_count.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_counter_get_count.restype = ct.c_int

    def getCount(self, channel: int) -> int:
        """
        Reads the counter value of a quadrature decoder. 
        Channel number must be 0 < channel < nof available channels.
        
        Parameters
        ----------
        channel : channel number 
        
        Returns
        -------
        counter value
        """
        data = ct.c_uint32()
        error = self.dev.lib.flink_counter_get_count(self.subDev, channel, ct.byref(data))
        if error < 0:
            raise flink.FlinkException("Failed to get data in counter subdevice", error, self.subDev)
        val = ct.c_int16(data.value)
        return numpy.int16(val)
