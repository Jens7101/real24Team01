import ctypes as ct
import threading
import flink
import typing

__author__ = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

FlinkDevice = typing.NewType("FlinkDevice", None)
FlinkSubDevice = typing.NewType("FlinkSubDevice", None)

class FlinkException(Exception):
    def __init__(self, description: str, error: int, subDev = None):
        super().__init__(description)
        self.errorValue = error
        self.subDev = subDev
        
class FileException(Exception):
    def __init__(self, description: str):
        super().__init__(description)

class FlinkSubDevice:
    """
    A flink subdevice is the base class for any of the implemented flink subdevices.
    Subdevices could be GPIO, PWM, UART ...
    """

    def __init__(self, dev: FlinkDevice, subDev: ct.c_void_p):
        self.dev = dev          # handle to flink device which incorporates this subdevice
        self.subDev = subDev    # handle to subdevice within flink, points to struct within lib 
        self.dev.lib.flink_subdevice_get_id.argtypes = [ct.c_void_p]
        self.dev.lib.flink_subdevice_get_id.restype = ct.c_uint8
        self.dev.lib.flink_subdevice_get_function.argtypes = [ct.c_void_p]
        self.dev.lib.flink_subdevice_get_function.restype = ct.c_uint16
        self.dev.lib.flink_subdevice_get_subfunction.argtypes = [ct.c_void_p]
        self.dev.lib.flink_subdevice_get_subfunction.restype = ct.c_uint8
        self.dev.lib.flink_subdevice_get_function_version.argtypes = [ct.c_void_p]
        self.dev.lib.flink_subdevice_get_function_version.restype = ct.c_uint8
        self.dev.lib.flink_subdevice_get_memsize.argtypes = [ct.c_void_p]
        self.dev.lib.flink_subdevice_get_memsize.restype = ct.c_uint32
        self.dev.lib.flink_subdevice_get_nofchannels.argtypes = [ct.c_void_p]
        self.dev.lib.flink_subdevice_get_nofchannels.restype = ct.c_uint32
        self.dev.lib.flink_subdevice_get_unique_id.argtypes = [ct.c_void_p]
        self.dev.lib.flink_subdevice_get_unique_id.restype = ct.c_uint32
        self.dev.lib.flink_subdevice_reset.argtypes = [ct.c_void_p]
        self.dev.lib.flink_subdevice_reset.restype = ct.c_int
        self.dev.lib.flink_subdevice_select.argtypes = [ct.c_void_p, ct.c_uint8]
        self.dev.lib.flink_subdevice_select.restype = ct.c_int
        self.dev.lib.flink_subdevice_id2str.argtypes = [ct.c_uint8]
        self.dev.lib.flink_subdevice_id2str.restype = ct.c_char_p
        self.dev.lib.flink_read.argtypes = [ct.c_void_p, ct.c_int, ct.c_uint8, ct.c_void_p]
        self.dev.lib.flink_read.restype = ct.c_ssize_t
        self.dev.lib.flink_write.argtypes = [ct.c_void_p, ct.c_int, ct.c_uint8, ct.c_void_p]
        self.dev.lib.flink_write.restype = ct.c_ssize_t
        self.dev.lib.flink_read_bit.argtypes = [ct.c_void_p, ct.c_int, ct.c_uint8, ct.c_void_p]
        self.dev.lib.flink_read_bit.restype = ct.c_int
        self.dev.lib.flink_write_bit.argtypes = [ct.c_void_p, ct.c_int, ct.c_uint8, ct.c_void_p]
        self.dev.lib.flink_write_bit.restype = ct.c_int

    # ===================== Functions to read fields common to all subdevice =====================

    def getId(self) -> int:
        """
        Get the id of this subdevice.

        Returns
        -------
        id of the subdevice
        """
        return self.dev.lib.flink_subdevice_get_id(self.subDev)
    
    def getBaseAddr(self) -> None:
        """
        Get the base address of this subdevice

        Returns
        -------
        base address of this subdevice
        """
        return self.dev.lib.flink_subdevice_get_baseaddr(self.subDev)
        
    def getFunction(self) -> int:
        """
        Get the function of this subdevice

        Returns
        -------
        function code of the subdevice
        """
        return self.dev.lib.flink_subdevice_get_function(self.subDev)

    def getSubType(self) -> int:
        """
        Get the subtype of this subdevice

        Returns
        -------
        subtype of this subdevice
        """
        return self.dev.lib.flink_subdevice_get_subfunction(self.subDev)
        
    def getFunctionVersion(self) -> int:
        """
        Get the interface version of this subdevice

        Returns
        -------
        interface version of this subdevice
        """
        return self.dev.lib.flink_subdevice_get_function_version(self.subDev)

    def getMemSize(self) -> int:
        """
        Get the memory size of this subdevice

        Returns
        -------
        memory size of this subdevice
        """
        return self.dev.lib.flink_subdevice_get_memsize(self.subDev)

    def getNofChannels(self) -> int:
        """
        Get the number of channels of this subdevice.
        
        Returns
        -------
        number of channels
        """
        return self.dev.lib.flink_subdevice_get_nofchannels(self.subDev)

    def getUniqueId(self) -> int:
        """
        Get the unique id of this subdevice

        Returns
        -------
        unique id of this subdevice
        """
        return self.dev.lib.flink_subdevice_get_unique_id(self.subDev)
    
    def reset(self) -> None:
        """
        Resets this subdevice. Asserts reset bit in config register.

        Returns
        -------
        None
        """
        error = self.dev.lib.flink_subdevice_reset(self.subDev)
        if error < 0:
            raise FlinkException("Reset failed", error, self.subDev)

    def select(self, exclusive: bool) -> None:
        """
        Select a flink subdevice for further operations.

        Parameters
        ----------
        exclusive : block access to this subdevice for other processes 
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_subdevice_select(self.subDev, exclusive)
        if error < 0:
            raise FlinkException("Could not select subdevice", error, self.subDev)

    def id2str(self) -> str:
        """
        Returns the name of the subdevice.

        Returns
        -------
        id : id of theparam flink_subdev_id: 
        :type flink_subdev_id: uint8
        :return: name of the subdevice
        :rtype: String
        
        :raises Exception: If initialization isn't complete
        :raises FileException: Appears if the flink file has not been opened for the time being
        """
        return self.dev.lib.flink_subdevice_id2str(self.getId()).decode('utf-8')

    # ======================= Low level operations common to all subdevice =======================

    def _read(self, offset: int, size: int) -> int:
        """
        This low level function allows to read several bytes - typically a word - 
        from this subdevice.
        
        Parameters
        ----------
        offset : memory offset from where the reading happens 
        size : nof bytes to read
        
        Returns
        -------
        value read from memory
        """
        val = ct.pointer(ct.c_int())
        nofBytes = self.dev.lib.flink_read(self.subDev, offset, size, val)
        if nofBytes < 0:
            raise FlinkException("Error in low level read command", nofBytes, self)
        return val.contents.value

    def _write(self, offset: int, size: int, val: int) -> None:
        """
        This low level function allows to write several bytes - typically a word - 
        to this subdevice.
        
        Parameters
        ----------
        offset : memory offset to where the writing happens 
        size : nof bytes to write
        val : value to write
        
        Returns
        -------
        None
        """
        data = ct.pointer(ct.c_int(val))
        nofBytes = self.dev.lib.flink_write(self.subDev, offset, size, data)
        if nofBytes < 0:
            raise FlinkException("Error in low level write command", nofBytes, self)

    def _readBit(self, offset: int, bit: int) -> bool:
        """
        This low level function reads a single bit from this subdevice

        Parameters
        ----------
        offset : read offset, relative to the subdevice base address 
        bit : bit number
        
        Returns
        -------
        state of the bit
        """
        val = ct.pointer(ct.c_uint8())
        error = self.dev.lib.flink_read_bit(self.subDev, offset, bit, val)
        if error < 0:
            raise FlinkException("Error in low level read bit command", error, self)
        return bool(val.contents.value)
        
    def _writeBit(self, offset: int, bit: int, data: bool) -> None:
        """
        This low level function writes a single bit to this subdevice

        Parameters
        ----------
        offset : read offset, relative to the subdevice base address 
        bit : bit number
        data : state of the bit
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_write_bit(self.subDev, offset, bit, data)
        if error < 0:
            raise FlinkException("Error in low level write bit command", error, self)



class FlinkDevice:
    """
    A flink device is a hardware configuration in a FPGA device, 
    see www.flink-project.ch. 
    It offers a multitude of specific subdevice with unique functionalities.
    """

    _instance = None

    def __init__(self, devFileName: str = "/dev/flink0", libPath: str = "/usr/lib/libflink.so"):
        """
        Creates a FlinkDevice. This is a Singleton! If the FlinkDevice already exists, it will 
        simply return the already existing instance.

        Parameters
        ----------
        devFileName : device file name of the flink device
        libPath : path to the flink library

        """
        self.lib = ct.CDLL(libPath)
        self.fileOpen = False
        self._openedFiles = ['']
        # open device file, scans all subdevices, set self.dev as a pointer to struct within lib
        self.open(devFileName) 
        self.lib.flink_get_nof_subdevices.argtypes = [ct.c_void_p]
        self.lib.flink_get_nof_subdevices.restype = ct.c_int
        self.lib.flink_get_subdevice_by_id.argtypes = [ct.c_void_p, ct.c_uint8]
        self.lib.flink_get_subdevice_by_id.restype = ct.c_void_p
        self.lib.flink_get_subdevice_by_unique_id.argtypes = [ct.c_void_p, ct.c_uint32]
        self.lib.flink_get_subdevice_by_unique_id.restype = ct.c_void_p
        self.lib.flink_open.argtypes = [ct.c_char_p]
        self.lib.flink_open.restype = ct.c_void_p
        self.lib.flink_close.argtypes = [ct.c_void_p]
        self.lib.flink_close.restype = ct.c_int
        self.lib.flink_ioctl.argtypes = [ct.c_void_p, ct.c_int, ct.c_uint8, ct.c_void_p]
        self.lib.flink_ioctl.restype = ct.c_int

    def __new__(cls):
        """
        Do not call this manually. This will be called automatically
        """
        if cls._instance is None:
            with threading.Lock():
                if cls._instance is None:
                    cls._instance = super(FlinkDevice, cls).__new__(cls)
        return cls._instance

    def __del__(self):
        """
        Do not call this manually. This will be called automatically
        """
        if self.fileOpen:
            self.close()

    def open(self, fileName: str = "/dev/flink0") -> None:
        """
        Opens a flink device file

        Parameters
        ----------
        fileName : device file name of the flink device

        Returns
        ----------
        None
        """
        if self.fileOpen: 
            return
        if fileName in self._openedFiles:
            raise Exception("Shared lib already open")
        self.dev = self.lib.flink_open(fileName.encode("utf-8"))
        if self.dev is None:
            raise FlinkException("Failed to open flink device", -1)        
        self._openedFiles.append(fileName)
        self.fileName = fileName
        self.fileOpen = True  

    def close(self) -> None:
        """
        Closes an open flink device
        
        Returns
        ----------
        None
        """
        if self.fileOpen:
            error = self.lib.flink_close(self.dev)
            if error != 0:
                raise FlinkException("Something went wrong while closing device", error)
            self._openedFiles.remove(self.fileName)
            self.dev = None
            self.fileOpen = False

    def getNofSubDevices(self) -> int:
        """
        Returns the number of subdevices of this flink device.
 
        Returns
        ----------
        the number of subdevices
        """
        nofSubDev = self.lib.flink_get_nof_subdevices(self.dev)
        if nofSubDev < 0:
            raise FlinkException("Error while getting numbers of subdevices", nofSubDev)
        return nofSubDev
    
    def getSubDeviceById(self, id: int) -> ct.c_void_p:
        """
        Find subdevice of this flink device with a given id

        Parameters
        ----------
        id : id of subdevice
        
        Returns
        -------
        subdevice with given id
        """
        subDev = self.lib.flink_get_subdevice_by_id(self.dev, id)
        if subDev is None:
            raise FlinkException("Failed to get subdevice", -1) 
        return subDev

    def getSubDeviceByUniqueId(self, id: int) -> ct.c_void_p:
        """
        Find subdevice of this flink device with a given unique id

        Parameters
        ----------
        id : unique id of subdevice
        
        Returns
        -------
        subdevice with given unique id
        """
        subDev = self.lib.flink_get_subdevice_by_unique_id(self.dev, id)
        if subDev is None:
            raise FlinkException("Failed to get subdevice", -1) 
        return subDev

    def getSubdeviceByType(self, type: int, subType: int = 0) -> ct.c_void_p:
        """
        Find subdevice of this flink device with a given type and subtype.
        
        Parameters
        ----------
        type : type of the subdevice 
        subType : subtype of the subdevice
        
        Returns
        -------
        the found subdevice or None if not found
        """
        for i in range(self.getNofSubDevices()):
            subDev = self.getSubDeviceById(i)
            if self.lib.flink_subdevice_get_function(subDev) == type and self.lib.flink_subdevice_get_subfunction(subDev) == subType:
                return subDev
        errString = "Failed to get subdevice with type" + str(type) + " and subtype" + str(subType)
        raise FlinkException(errString, -1)
        return # type: ignore
    
    #TODO: replace with id2str
    def __idToCharArray(self, id: int) -> str:
        if id == flink.Definitions.PWM_INTERFACE_ID: return "PWM"
        elif id == flink.Definitions.GPIO_INTERFACE_ID: return "GPIO"
        elif id == flink.Definitions.COUNTER_INTERFACE_ID: return "FQD"
        elif id == flink.Definitions.WD_INTERFACE_ID: return "WATCHDOG"
        elif id == flink.Definitions.UART_INTERFACE_ID: return "UART"
        elif id == flink.Definitions.PPWA_INTERFACE_ID: return "PPWA"
        elif id == flink.Definitions.STEPPER_MOTOR_INTERFACE_ID: return "STEPPER MOTOR"
        elif id == flink.Definitions.SENSOR_INTERFACE_ID: return "SENSOR"
        elif id == flink.Definitions.IRQ_MULTIPLEXER_INTERFACE_ID: return "IRQ MULTIPLEXER"
        elif id == flink.Definitions.ANALOG_INPUT_INTERFACE_ID: return "ANALOG INPUT"
        elif id == flink.Definitions.ANALOG_OUTPUT_INTERFACE_ID: return "ANALOG OUTPUT"
        elif id == flink.Definitions.INFO_DEVICE_ID: return "INFO DEVICE"
        else: return str(id)
	
    def lsflink(self):
        """
        Prints the content of a flink device with all its subdevices to standard out.
        
        Returns
        -------
        None
        """
        print("Subdevices of flink device:")
        for i in range(self.getNofSubDevices()):
            s = self.getSubDeviceById(i)
            addr = self.lib.flink_subdevice_get_baseaddr(s)
            size = self.lib.flink_subdevice_get_memsize(s)
            print("\tsubdev", i, ": address range:", hex(addr), " - ", hex(addr + size - 1), end = '')
            print(" memory size:", size, " function:", self.__idToCharArray(self.lib.flink_subdevice_get_function(s)), end = '')
            print(" subtype:", self.lib.flink_subdevice_get_subfunction(s), " function version", self.lib.flink_subdevice_get_function_version(s), end = '')
            print(" nof channels:", self.lib.flink_subdevice_get_nofchannels(s), "unique id:", self.lib.flink_subdevice_get_unique_id(s))

    # ========================== Low level operations of a flink device ==========================

    def ioctl(self, cmd: int, arg: ct.c_void_p) -> int:
        """
        IOCTL operation for a flink device.

        Parameters
        ----------
        cmd : IOCTL command 
        arg : IOCTL arguments
        
        Returns
        -------
        IOCTL return value or -1 in case of failure
        """
        ioctl = self.lib.flink_ioctl(self.dev, cmd, arg)
        if ioctl < 0:
            raise FlinkException("Error in ioctl command", ioctl)
        return ioctl
