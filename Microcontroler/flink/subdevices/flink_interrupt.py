import flink
import ctypes as ct
import signal

__author__  = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkInterrupt(flink.FlinkSubDevice):
    """
    This class provides IRQ functionality to register a function on an IRQ and to configure the IRQ multiplexer subdevice.
    
    IRQ multiplexer:
        The multiplexer can be used to select which FLINK IRQ is connected to an IRQ line.
    """

    def __init__(self):
        """
        Creates a interrupt object.
        
        Parameters
        ----------
        
        Returns
        -------
        the object
        """
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.IRQ_MULTIPLEXER_INTERFACE_ID)
        super().__init__(dev, subDev)
        dev.lib.flink_register_irq.argtypes = [ct.c_void_p, ct.c_uint32]
        dev.lib.flink_register_irq.restype = ct.c_int
        dev.lib.flink_unregister_irq.argtypes = [ct.c_void_p, ct.c_uint32]
        dev.lib.flink_unregister_irq.restype = ct.c_int  
        dev.lib.flink_get_signal_offset.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_get_signal_offset.restype = ct.c_int
        dev.lib.flink_set_irq_multiplex.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_set_irq_multiplex.restype = ct.c_int
        dev.lib.flink_get_irq_multiplex.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_get_irq_multiplex.restype = ct.c_int
        self.registeredIRQ = {}

    def registerIRQ(self, irq: int, callback: callable) -> None:
        """
        Registering an IRQ in the kernel and associating it with a function
        
        Parameters
        ----------
        irq      : The IRQ number to connect with the function
        callback : The function to connect with the IRQ number
        
        Returns
        -------
        None
        """
        if irq in self.registeredIRQ:
            raise flink.FlinkException("IRQ: {irq} already used with function: {callback.__name__}", None, None)

        if not callable(callback):
            raise TypeError("Callback function isn't of type callable")

        sigNr = self.dev.lib.flink_register_irq(self.dev.dev, irq)
        if sigNr < 0:
            raise flink.FlinkException("Failed to register IRQ {irq}", sigNr, None)
        signal.signal(sigNr, callback)
        self.registeredIRQ[irq] = (sigNr, callback)


    def unregisterIRQ(self, irq: int) -> None:
        """
        Unregistering an IRQ in the kernel and deassociating it with the function
        
        Parameters
        ----------
        irq : The IRQ number to disconnect
        
        Returns
        -------
        None
        """
        if irq not in self.registeredIRQ:
            raise flink.FlinkException("IRQ: {irq} isn't used, yet", None, None)
        sigNr, callback = self.registeredIRQ.get(irq)

        error = self.dev.lib.flink_unregister_irq(self.dev.dev, irq)
        if error < 0:
            self.registeredIRQ[irq] = (sigNr, callback)
            raise flink.FlinkException("Failed to unregister IRQ: {irq} with function {callback.__name__}", error, None)
        signal.signal(sigNr, signal.SIG_DFL)
        del self.registeredIRQ[irq]
    
    def setIRQmultiplexerValue(self, irq: int, flink_irq: int) -> None:
        """
        Connet an flink IRQ to an IRQ.
        flink IRQ is an IRQ line coming from a flink subdevice.
        IRQ is the IRQ line going to the interrupt controller.
        
        Parameters
        ----------
        irq : IRQ number
        flink_irq : flink IRQ Number
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_set_irq_multiplex(self.subDev, irq, flink_irq)
        if error < 0:
            raise flink.FlinkException("Failed to connect the fink IRQ Nr: {flink_irq} to the IRQ Nr: {irq}", error, self.subDev)
        
    def getIRQmultiplexerValue(self, irq: int) -> int:
        """
        Reads the connection of an IRQ to its flink IRQ.
        flink IRQ is an IRQ line coming from a flink subdevice.
        IRQ is the IRQ line going to the interrupt controller.
        
        Parameters
        ----------
        irq : IRQ number
        flink_irq : flink IRQ Number
        
        Returns
        -------
        flink IRQ Number
        """
        flink_irq = ct.c_uint32()
        error = self.dev.lib.flink_get_irq_multiplex(self.subDev, irq, flink_irq)
        if error < 0:
            raise flink.FlinkException("Failed to read connection of the IRQ Nr: {irq}", error, self.subDev)
        return int(flink_irq.value)
        
    def _getSignalOffset(self) -> int:
        """
        Get the signal offset which is sent by the kernel.
        
        Parameters
        ----------
        
        Returns
        -------
        The signal offset number
        """
        offset = ct.c_uint32()
        error = self.dev.lib.flink_get_signal_offset(self.subDev, offset)
        if error < 0:
            raise flink.FlinkException("Failed to read the signal offset", error, None)
        return int(offset.value)
        