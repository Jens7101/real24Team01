import flink
import ctypes as ct

__author__ = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkInfo(flink.FlinkSubDevice):
    """
    The flink Info subdevice is used the deliver a description string 
    for a flink device together with the total amount of used memory.
    """

    def __init__(self):
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.INFO_DEVICE_ID)
        super().__init__(dev, subDev)
        dev.lib.flink_info_get_description.argtypes = [ct.c_void_p, ct.c_char_p]
        dev.lib.flink_info_get_description.restype = ct.c_int
    
    def getMemLength(self) -> int:
        """
        Returns the total amount of memory mapped onto the AXI bus.
	    This memory covers the memory blocks of all subdevices within a flink device.
        
        Returns
        -------
        total memory size of flink device in bytes
        """
        size = self._read(0x20, 4)
        return size
        
    def getDescription(self) -> str:
        """
        A info device holds a description string which can describe a flink device.
        
        Returns
        -------
        desription string
        """
        p_string = ct.create_string_buffer(flink.Definitions.INFO_DESC_SIZE)
        error = self.dev.lib.flink_info_get_description(self.subDev, p_string)
        if error < 0:
            raise flink.FlinkException("Failed to read description from info subdevice", error, self.subDev)
        return p_string.value.decode('utf-8')

