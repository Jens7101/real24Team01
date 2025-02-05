import flink
import ctypes as ct
from typing import Tuple

__author__  = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkReflectiveSensor(flink.FlinkSubDevice):
    """
    The flink reflectivesensor subdevice realizes an reflective sensor within a flink device.
    It offers several channels. Each channel has it's own sensor value and a level for IRQ generating.
    
    For IRQ:
        - Each channel has two IRQ lines. one line when the sensor value exceeds the upper level
          and one line when the sensor value decreases below the lower level.
        - The configuration of the levels is done here, but to configure the IRQ with a  
          function use the FlinkInterrupt class.
    """

    def __init__(self):
        """
        Creates a reflective sensor object.
        
        Parameters
        ----------
        
        Returns
        -------
        the object
        """
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.SENSOR_INTERFACE_ID, flink.Definitions.REFLECTIVE_SENSOR_SUBTYP)
        super().__init__(dev, subDev)
        dev.lib.flink_reflectivesensor_get_resolution.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_reflectivesensor_get_resolution.restype = ct.c_int
        dev.lib.flink_reflectivesensor_get_value.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_reflectivesensor_get_value.restype = ct.c_int  
        dev.lib.flink_reflectivesensor_set_upper_level_int.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_reflectivesensor_set_upper_level_int.restype = ct.c_int
        dev.lib.flink_reflectivesensor_get_upper_level_int.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_reflectivesensor_get_upper_level_int.restype = ct.c_int
        dev.lib.flink_reflectivesensor_set_lower_level_int.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_reflectivesensor_set_lower_level_int.restype = ct.c_int
        dev.lib.flink_reflectivesensor_get_lower_level_int.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_reflectivesensor_get_lower_level_int.restype = ct.c_int
        self._RESOLUTION = self._getResolution()

    ##################################################################################
    # Internal methodes
    ##################################################################################
    def _getResolution(self) -> int:
        """
        Reads the resolution of a single channel within a reflective sensor subdevice. 
        Channel number must be 0 <= channel < nof available channels.
        
        Parameters
        ----------
        channel : channel number 
        
        Returns
        -------
        Resolution
        """
        val = ct.c_uint32()
        error = self.dev.lib.flink_reflectivesensor_get_resolution(self.subDev, val)
        if error < 0:
            raise flink.FlinkException("Failed read the resolution of the reflective sensor", error, self.subDev)
        return int(val.value)
    
    ##################################################################################
    # External methodes
    ##################################################################################
    def getResolution(self) -> int:
        """
        Reads the resolution of a single channel within a reflective sensor subdevice. 
        Channel number must be 0 <= channel < nof available channels.
        
        Parameters
        ----------
        channel : channel number 
        
        Returns
        -------
        Resolution
        """
        return self._RESOLUTION

    def getValue(self, channel: int) -> int:
        """
        Reads the value of a single channel within a reflective sensor subdevice. 
        Channel number must be 0 <= channel < nof available channels.
        
        Parameters
        ----------
        channel : channel number 
        
        Returns
        -------
        Sensor value in digitised steps between 0 and Resolution
        """
        val = ct.c_uint32()
        error = self.dev.lib.flink_reflectivesensor_get_value(self.subDev, channel, val)
        if error < 0:
            raise flink.FlinkException("Failed to read value from reflective sensor channel", error, self.subDev)
        return int(val.value)

    def setLevel(self, channel: int, upperBound: int, lowerBound: int) -> None:
        """
        Writes the upper and lower level of a single channel. 
        Channel number must be 0 <= channel < nof available channels.
        Bounds must be 0 <= upperBound, lowerBound <= resolution
        
        Parameters
        ----------
        channel    : channel number
        upperBound : The upper level
        lowerBound : The lower level
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_reflectivesensor_set_upper_level_int(self.subDev, channel, upperBound)
        if error < 0:
            raise flink.FlinkException("Failed to write upper level to channel", error, self.subDev)
        error = self.dev.lib.flink_reflectivesensor_set_lower_level_int(self.subDev, channel, lowerBound)
        if error < 0:
            raise flink.FlinkException("Failed to write lower level to channel", error, self.subDev)
        
    def getLevel(self, channel: int) -> Tuple[int, int]:
        """
        Reads the upper and lower level of a single channel. 
        Channel number must be 0 <= channel < nof available channels.
        Bounds must be 0 <= upperBound, lowerBound <= resolution
        
        Parameters
        ----------
        channel    : channel number
        
        Returns
        -------
        (lowerBound, upperBound)
        lowerBound : The lower level
        upperBound : The upper level
        """

        upperBound = ct.c_uint32()
        lowerBound = ct.c_uint32()
        error = self.dev.lib.flink_reflectivesensor_get_upper_level_int(self.subDev, channel, upperBound)
        if error < 0:
            raise flink.FlinkException("Failed to read upper level of channel", error, self.subDev)
        error = self.dev.lib.flink_reflectivesensor_get_lower_level_int(self.subDev, channel, ct.byref(lowerBound))
        if error < 0:
            raise flink.FlinkException("Failed to read lower level of channel", error, self.subDev)
        return (int(lowerBound.value), int(upperBound.value))
        