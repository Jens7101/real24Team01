import flink
import ctypes as ct

__author__ = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkPPWA(flink.FlinkSubDevice):
    """
    The flink PPWA subdevice realizes a PPWA (pulse and period measurement) function within a flink device.
    It offers several channels. Each channel functions on its own.
    """

    def __init__(self):
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.PPWA_INTERFACE_ID)
        super().__init__(dev, subDev)
        dev.lib.flink_ppwa_get_baseclock.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_ppwa_get_baseclock.restype = ct.c_int
        dev.lib.flink_ppwa_get_period.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_ppwa_get_period.restype = ct.c_int
        dev.lib.flink_ppwa_get_hightime.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_ppwa_get_hightime.restype = ct.c_int

    def getBaseClock(self) -> int:
        """
        Returns the base clock of the underlying hardware counter.
        
        Returns
        -------
        The base clock in Hz
        """
        clk = ct.c_uint32()
        error = self.dev.lib.flink_ppwa_get_baseclock(self.subDev, ct.byref(clk))
        if error < 0:
            raise flink.FlinkException("Failed to get baseclock from ppwm subdevice", error, self.subDev)
        return clk.value

        return self.flink.flink_ppwa_get_baseclock(self.subDev)

    def getPeriod(self, channel: int) -> int:
        """
        Reads the period of a single channel. Channel number
	    must be 0 <= channel < nof available channels. Period setting is
	    in multiple of the base clock, see getBaseClock().
        
        Parameters
        ----------
        channel : channel number 
        
        Returns
        -------
        multiple of base clock
        """
        period = ct.c_uint32()
        error = self.dev.lib.flink_ppwa_get_period(self.subDev, channel, ct.byref(period))
        if error < 0:
            raise flink.FlinkException("Failed to get period from ppwm subdevice", error, self.subDev)
        return period.value

    def getHighTime(self, channel: int) -> int:
        """
        Reads the hightime of a single channel. Channel number
	    must be 0 <= channel < nof available channels. Hightime setting is
	    in multiple of the base clock, see getBaseClock().
        
        Parameters
        ----------
        channel : channel number 
        
        Returns
        -------
        multiple of base clock
        """
        hightime = ct.c_uint32()
        error = self.dev.lib.flink_ppwa_get_hightime(self.subDev, channel, ct.byref(hightime))
        if error < 0:
            raise flink.FlinkException("Failed to get baseclock from ppwm subdevice", error, self.subDev)
        return hightime.value
