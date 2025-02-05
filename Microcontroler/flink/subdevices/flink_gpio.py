import flink
import ctypes as ct

__author__ = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkGPIO(flink.FlinkSubDevice):
    """
    The flink GPIO subdevice realizes digital input and output within a flink device.
    It offers several channels. Each channel drives a single pin.
    """

    def __init__(self):
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.GPIO_INTERFACE_ID)
        super().__init__(dev, subDev)
        dev.lib.flink_dio_get_baseclock.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_dio_get_baseclock.restype = ct.c_int
        dev.lib.flink_dio_set_direction.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint8]
        dev.lib.flink_dio_set_direction.restype = ct.c_int
        dev.lib.flink_dio_set_value.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint8]
        dev.lib.flink_dio_set_value.restype = ct.c_int  
        dev.lib.flink_dio_get_value.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint8)]
        dev.lib.flink_dio_get_value.restype = ct.c_int
        dev.lib.flink_dio_set_debounce.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_dio_set_debounce.restype = ct.c_int
        dev.lib.flink_dio_get_debounce.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_dio_get_debounce.restype = ct.c_int
        self._BASE_CLOCK = self._getBaseclock()

    ##################################################################################
    # Internal methodes
    ##################################################################################
    def _getBaseclock(self) -> int:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Returns the base clock of the underlying hardware.
        
        Parameters
        ----------
        channel : channel number 
        value : false = input, true = output
        
        Returns
        -------
        Baseclock in Hz
        """
        baseClock = ct.c_uint32()
        error = self.dev.lib.flink_dio_get_baseclock(self.subDev, ct.byref(baseClock))
        if error < 0:
            raise flink.FlinkException("Failed to read the base clock of gpio", error, self.subDev)
        return int(baseClock.value)
    
    ##################################################################################
    # External methodes
    ##################################################################################
    def getBaseclock(self) -> int:
        """
        Returns the base clock of the underlying hardware.
        
        Parameters
        ----------
        channel : channel number 
        value : false = input, true = output
        
        Returns
        -------
        Baseclock in Hz
        """
        return self._BASE_CLOCK

    def setDir(self, channel: int, out: bool) -> None:
        """
        Sets the direction of a single channel within a GPIO subdevice. 
        Each channel can work as either digital input or output. 
        Channel number must be 0 < channel < nof available channels.
        
        Parameters
        ----------
        channel : channel number 
        value : false = input, true = output
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_dio_set_direction(self.subDev, channel, out)
        if error < 0:
            raise flink.FlinkException("Failed to set direction of gpio channel", error, self.subDev)

    def getValue(self, channel: int) -> bool:
        """
        Reads the value of a single channel within a GPIO subdevice. 
        Each channel can work as either digital input or output. 
        Channel number must be 0 < channel < nof available channels.
        
        Parameters
        ----------
        channel : channel number 
        
        Returns
        -------
        false = input, true = output
        """
        val = ct.c_uint8()
        error = self.dev.lib.flink_dio_get_value(self.subDev, channel, ct.byref(val))
        if error < 0:
            raise flink.FlinkException("Failed to read from gpio channel", error, self.subDev)
        return bool(val.value)

    def setValue(self, channel: int, val: bool) -> None:
        """
        Sets the logical level of a single channel within a GPIO subdevice. 
        Channel number must be 0 < channel < nof available channels.
        
        Parameters
        ----------
        channel : channel number 
        value : false = low, true = high
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_dio_set_value(self.subDev, channel, val)
        if error < 0:
            raise flink.FlinkException("Failed to set value of gpio channel", error, self.subDev)
        
    def setDebounce(self, channel: int, debounce: int) -> None:
        """
        Sets the debounce time of a channel for IRQ functionality.
        This prevents multiple IRQs from being triggered when the input bounces.
        
        Parameters
        ----------
        channel : channel number 
        debounce : debounce time. In multiple of base clock
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_dio_set_debounce(self.subDev, channel, debounce)
        if error < 0:
            raise flink.FlinkException("Failed to set debounce of gpio channel", error, self.subDev)
        
    def getDebounce(self, channel: int) -> int:
        """
        Gets the debounce time of a channel for IRQ functionality.
        This prevents multiple IRQs from being triggered when the input bounces.
        
        Parameters
        ----------
        channel : channel number 
        
        Returns
        -------
        Debounce time. In multiple of base clock
        """
        debounce = ct.c_uint32()
        error = self.dev.lib.flink_dio_get_debounce(self.subDev, channel, debounce)
        if error < 0:
            raise flink.FlinkException("Failed to get debounce of gpio channel", error, self.subDev)
        return int(debounce.value)
        