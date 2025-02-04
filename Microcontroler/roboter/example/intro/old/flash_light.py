import time
import threading
import flink

gpio = flink.FlinkGPIO()

stopEvent = threading.Event()

def flash(gpio: flink.FlinkGPIO):
    ledPin = 5
    gpio.setDir(ledPin, True)
    gpio.setValue(ledPin, False)
    while True:
        gpio.setValue(ledPin, not gpio.getValue(ledPin))
        time.sleep(0.5)
        if (stopEvent.is_set()):
            break
        
gpio = flink.FlinkGPIO()
t1 = threading.Thread(target=flash, args=(gpio,))
t1.start()

try:
    while 1:
        time.sleep(.1)
except KeyboardInterrupt:
    stopEvent.set()
    t1.join()