import driver
import time

disp = driver.HD44780U()
disp.init(2)
a = 87103
disp.writeString(str(a))
disp.setCursor(1,5)
disp.writeChar('A')
disp.writeChar('x')
time.sleep(3)
disp.clearDisplay()
disp.onOff(True, False, False)
disp.writeString("hello")
time.sleep(3)
disp.setCursor(1,3)
disp.writeString("again")
disp.setCursor(0, 8)
disp.onOff(True, True, True)
disp.writeChar('q')
time.sleep(3)
disp.clearDisplay()
disp.onOff(False, False, False)
disp.writeChar('q')

