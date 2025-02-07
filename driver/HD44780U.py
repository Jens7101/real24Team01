import flink
import time

class HD44780U:
    """
    Driver for character display with 2 - 4 rows and 16 columns.
    
    Display controller: HD44780U
    Connected to flink gpios of the Zynq7000:
    GPIO:     Display:
    gpio[0]   D0 (data line)
    gpio[1]   D1 (data line)
    gpio[2]   D2 (data line)
    gpio[3]   D3 (data line)
    gpio[4]   D4 (data line)
    gpio[5]   D5 (data line)
    gpio[6]   D6 (data line)
    gpio[7]   D7 (data line)
    gpio[8]   RS (Data/Instruction)
    gpio[9]   E (Enable)
    gpio[10]  R/W' (Read/Write)
    
    Base setting: Display On, Cursor On, Blink On, Increment, no shift
    """

    __author__ = "Urs Graf"
    __license__ = "http://www.apache.org/licenses/LICENSE-2.0"
    __version__ = "1.0"
    MAX_ROWS = 2
    MAX_COLUMNS = 16
    RS = 8
    E = 9
    RW = 10
    
    def __init__(self):
        self.gpio = flink.FlinkGPIO()
        self.adrCntOfRow = [0x80, 0xC0, 0x90, 0xD0]
        
    def init(self, nofRows: int) -> None:
        """
        Initialisation of the display.

        Parameters
        ----------
	    nofRows : number of rows present in the display: 2, 3 or 4.

        Returns
        -------
        None
        """
        self.gpio.setDir(self.RS, True)
        self.gpio.setDir(self.E, True)
        self.gpio.setDir(self.RW, True)
        self.gpio.setValue(self.RS, False)
        self.gpio.setValue(self.E, False)
        self.gpio.setValue(self.RW, False)

        if (nofRows < 2): nofRows = 2
        elif (nofRows > 4): nofRows = 4
        self.maxRows = nofRows
        self.cursPos = 0
		
        self.__writeCmd(0x30)
        time.sleep(0.01)
        self.__writeCmd(0x30)
        time.sleep(0.01)
        self.__writeCmd(0x30)
        while self.__readStatus() & 0x80 != 0: pass
        self.__writeCmd(0x38)
        while self.__readStatus() & 0x80 != 0: pass
        self.__writeCmd(0x38)
        while self.__readStatus() & 0x80 != 0: pass
        self.__writeCmd(0x38)
        while self.__readStatus() & 0x80 != 0: pass
        self.__writeCmd(0x1)
        while self.__readStatus() & 0x80 != 0: pass
        self.__writeCmd(0xF)
        while self.__readStatus() & 0x80 != 0: pass
        self.__writeCmd(0x6)
        while self.__readStatus() & 0x80 != 0: pass
        self.__writeCmd(0x2)
        while self.__readStatus() & 0x80 != 0: pass

    def setCursor(self, row: int, column: int) -> None:
        """
        Sets the cursor on desired destination.
        
        Parameters
        ----------
        row : row, starting with row 0. 
        column : column, starting with 0.
        
        Returns
        -------
        None
        """
        row = (row % self.MAX_ROWS)
        column = (column % self.MAX_COLUMNS)
        self.cursPos = (row * self.MAX_COLUMNS + column)
        self.__writeCmd((self.adrCntOfRow[row] + column))

    def writeChar(self, ch: str) -> None:
        """
        Writes a character on the display at current cursor position.
        
        Parameters
        ----------
        ch : character to write. 
        
        Returns
        -------
        None
        """
		
        self.__writeData(ord(ch))
        self.cursPos += 1
        if self.cursPos % self.MAX_COLUMNS == 0:
            self.cursPos = (self.cursPos % (self.maxRows * self.MAX_COLUMNS))
            self.setCursor((int)(self.cursPos / self.MAX_COLUMNS), self.cursPos)

    def writeString(self, s: str) -> None:
        """
        Writes a string on the display at current cursor position.
        
        Parameters
        ----------
        s : string to write. 
        
        Returns
        -------
        None
        """
        for i in range(len(s)):
            self.writeChar(s[i])

    def clearDisplay(self) -> None:
        """
        Clears the display and sets the cursor to position 0,0.
        
        Returns
        -------
        None
        """
        self.cursPos = 0
        self.__writeCmd(1)
        while self.__readStatus() & 0x80 != 0: pass

    def onOff(self, displayOn: bool, cursorOn: bool, blinkOn: bool) -> None:
        """
        Controls display properties. Display, cursor and blinking can be switched on or off.
        
        Parameters
        ----------
        displayOn : True -> display on, False -> display off 
        cursorOn : True -> cursor on, False -> cursor off 
        blinkOn : True -> blinking of cursor position on, False -> blinking off 
        
        Returns
        -------
        None
        """
        val = 8
        if displayOn: val += 4
        if cursorOn: val += 2
        if blinkOn: val += 1
        self.__writeCmd(val)
        while self.__readStatus() & 0x80 != 0: pass

    def __writeCmd(self, cmd: int):
        self.gpio.setValue(self.RS, False)
        self.gpio.setValue(self.RW, False)
        self.gpio.setValue(self.E, True)
        self.__writeBus(cmd)
        self.gpio.setValue(self.E, False)

    def __writeData(self, data: int):
        self.gpio.setValue(self.RS, True)
        self.gpio.setValue(self.RW, False)
        self.gpio.setValue(self.E, True)
        self.__writeBus(data)
        self.gpio.setValue(self.E, False)

    def __writeBus(self, data: int):
        self.gpio._write(0x24, 1, 0xff)
        self.gpio._write(0x28, 1, data)

    def __readStatus(self) -> int:
        self.gpio.setValue(self.RS, False)
        self.gpio.setValue(self.RW, True)
        self.gpio.setValue(self.E, True)
        status = self.__readBus()
        self.gpio.setValue(self.E, False)
        return status
    
    def __readBus(self) -> int:
        self.gpio._write(0x24, 1, 0)
        data = self.gpio._read(0x28, 1)
        return data
