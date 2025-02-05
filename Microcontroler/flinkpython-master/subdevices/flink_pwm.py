import flink
import ctypes as ct

__author__ = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkPWM(flink.FlinkSubDevice):
    """
    The flink PWM subdevice realizes a PWM (pulse with modulation) function within a flink device.
    It offers several channels. Each channel has its own period and duty cycle.
    """

    def __init__(self):
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.PWM_INTERFACE_ID)
        super().__init__(dev, subDev)
        dev.lib.flink_pwm_get_baseclock.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_pwm_get_baseclock.restype = ct.c_int
        dev.lib.flink_pwm_set_period.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_pwm_set_period.restype = ct.c_int
        dev.lib.flink_pwm_get_period.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_pwm_get_period.restype = ct.c_int
        dev.lib.flink_pwm_set_hightime.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_pwm_set_hightime.restype = ct.c_int
        dev.lib.flink_pwm_get_hightime.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_pwm_get_hightime.restype = ct.c_int

    def getBaseClock(self) -> int:
        """
        Returns the base clock of the underlying hardware counter.
        
        Returns
        -------
        The base clock in Hz
        """
        clk = ct.c_uint32()
        error = self.dev.lib.flink_pwm_get_baseclock(self.subDev, ct.byref(clk))
        if error < 0:
            raise flink.FlinkException("Failed to get baseclock from pwm subdevice", error, self.subDev)
        return clk.value

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
        error = self.dev.lib.flink_pwm_get_period(self.subDev, channel, ct.byref(period))
        if error < 0:
            raise flink.FlinkException("Failed to get period in pwm subdevice", error, self.subDev)
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
        error = self.dev.lib.flink_pwm_get_hightime(self.subDev, channel, ct.byref(hightime))
        if error < 0:
            raise flink.FlinkException("Failed to get hightime in pwm subdevice", error, self.subDev)
        return hightime.value

    def setPeriod(self, channel: int, period: int) -> None:
        """
        Sets the period of a single channel. Channel number
	    must be 0 <= channel < nof available channels. Period setting is
	    in multiple of the base clock, see getBaseClock().
        
        Parameters
        ----------
        channel : channel number 
        period : multiple of base clock
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_pwm_set_period(self.subDev, channel, period)
        if error < 0:
            raise flink.FlinkException("Failed to set period in pwm subdevice", error, self.subDev)

    def setHighTime(self, channel: int, hightime: int) -> None:
        """
        Sets the hightime of a single channel. Channel number
	    must be 0 <= channel < nof available channels. Hightime setting is
	    in multiple of the base clock, see getBaseClock().
        
        Parameters
        ----------
        channel : channel number 
        hightime : multiple of base clock
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_pwm_set_hightime(self.subDev, channel, hightime)
        if error < 0:
            raise flink.FlinkException("Failed to set hightime in pwm subdevice", error, self.subDev)
