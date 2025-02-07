import flink

__author__ = "Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkUART(flink.FlinkSubDevice):
    """
    The flink UART subdevice realizes an UART function within a flink device.
    It offers several channels. Each channel has its own baudrate generator
    together with transmit and receive queues.
    """

    BASE_CLOCK_ADDRESS = 0x20
    DIVIDER_0_ADDRESS = BASE_CLOCK_ADDRESS + flink.Definitions.REGISTER_WIDTH
    TX_FULL = 6

    def __init__(self, uartNr: int):
        """
        Creates an UART subdevice.
        
        Parameters
        ----------
        uartNr : channel number of this UART instance

        Returns
        -------
        UART device
        """
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.UART_INTERFACE_ID)
        super().__init__(dev, subDev)
        self.divAddr = self.DIVIDER_0_ADDRESS + uartNr * flink.Definitions.REGISTER_WIDTH
        self.txAddr = self.divAddr + self.getNofChannels() * flink.Definitions.REGISTER_WIDTH
        self.rxAddr = self.txAddr + self.getNofChannels() * flink.Definitions.REGISTER_WIDTH
        self.statusAddr = self.rxAddr + self.getNofChannels() * flink.Definitions.REGISTER_WIDTH

    def start(self, baudRate: int) -> None:
        """
        Initialize and start the flink Universal Asynchronous Receiver Transmitter.
        This method has to be called before using the flink UART! The number of 
        stop bits, the parity mode and number of data bits can't be set.
        There is always one stop bit. Parity is off. Number of data bits is 8.
        
        Parameters
        ----------
        baudRate : the baud rate, allowed range: 64 to 1'000'000 bits/s

        Returns
        -------
        None
        """
        base = super()._read(self.BASE_CLOCK_ADDRESS, 4)
        super()._write(self.divAddr, 4, int(base / baudRate))

    def write(self, data: int) -> int:
        """
        Writes a given byte into the transmit buffer.
        If the buffer is full, the data is lost. You must check for the return value.
        
        Parameters
        ----------
        data : byte to write 
        
        Returns
        -------
        returns 1 if byte could be sent, else 0
        """
        status = self._read(self.statusAddr, 4)
        if (status & (1 << self.TX_FULL)) == 0: 
            self._write(self.txAddr, 4, data)
            return 1
        else:
            return 0

    def read(self) -> int:
        """
        Reads one byte from the UART. This call blocks until at least one byte is available.
        
        Returns
        -------
        byte read
        """
        # while self.availToRead() == 0: pass
        return self._read(self.rxAddr, 4)

    def availToRead(self) -> int:
        """
        Returns the number of bytes available in the receive buffer.
        
        Returns
        -------
        number of bytes in the receive buffer
        """
        return (self._read(self.statusAddr, 4) & 0xffffffff) >> 16
