import flink
import ctypes as ct

__author__ = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkWDT(flink.FlinkSubDevice):
    """
    The flink watchdog subdevice realizes a watchdog function within a flink device.
    """

    def __init__(self):
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.WD_INTERFACE_ID)
        super().__init__(dev, subDev)
        dev.lib.flink_wd_get_baseclock.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_wd_get_baseclock.restype = ct.c_int
        dev.lib.flink_wd_get_status.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint8)]
        dev.lib.flink_wd_get_status.restype = ct.c_int
        dev.lib.flink_wd_set_counter.argtypes = [ct.c_void_p, ct.c_uint32]
        dev.lib.flink_wd_set_counter.restype = ct.c_int
        dev.lib.flink_wd_arm.argtypes = [ct.c_void_p]
        dev.lib.flink_wd_arm.restype = ct.c_int

    def getBaseClock(self) -> int:
        """
        Returns the base clock of the underlying hardware counter.
        
        Returns
        -------
        The base clock in Hz
        """
        clk = ct.c_uint32()
        error = self.dev.lib.flink_wd_get_baseclock(self.subDev, ct.byref(clk))
        if error < 0:
            raise flink.FlinkException("Failed to get baseclock from watchdog subdevice", error, self.subDev)
        return clk.value
 
    def getStatus(self) -> int:
        """
        Reads the status register and returns the state of the status bit within.
        
        Returns
        -------
        true -> if watchdog is still running, false -> if watchdog has timed out
        """
        status = ct.c_uint8()
        error = self.dev.lib.flink_wd_get_status(self.subDev, ct.byref(status))
        if error < 0:
            raise flink.FlinkException("Failed to get status from watchdog subdevice", error, self.subDev)
        return status.value

    def setCounter(self, value: int) -> None:
        """
        Presets the watchdog counter. The value will be a multiple of the base clock.
        E.g. for a watchdog timeout of 100ms, you have to write a value of 0.1 * base clock 
        
        Parameters
        ----------
        value : counter value
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_wd_set_counter(self.subDev, value)
        if error < 0:
            raise flink.FlinkException("Failed to set the watchdog counter", error, self.subDev)

    def arm(self) -> None:
        """
        Starts the watchdog. If it has timed out, you have to arm again before it can run again.
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_wd_arm(self.subDev)
        if error < 0:
            raise flink.FlinkException("Faild to arm the watchdog timer", error, self.subDev)
