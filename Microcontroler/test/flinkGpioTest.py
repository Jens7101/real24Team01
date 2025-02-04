import flink
import time
import threading

stopEvent = threading.Event()

def toggle12():
    gpio = flink.FlinkGPIO()
    pin = 12
    gpio.setDir(pin, True)
    while True:
        gpio.setValue(pin, not gpio.getValue(pin))
        time.sleep(1)
        if (stopEvent.is_set()):
            break

def toggle13():
    gpio = flink.FlinkGPIO()
    pin = 13
    gpio.setDir(pin, True)
    while True:
        gpio.setValue(pin, not gpio.getValue(pin))
        time.sleep(1)
        if (stopEvent.is_set()):
            break

t1 = threading.Thread(target=toggle12)
t2 = threading.Thread(target=toggle13)

info = flink.FlinkInfo()
print("Info device: total memory size =", hex(info.getMemLength()))
print("Info device: description =", info.getDescription())

t1.start()
t2.start()
try:
    while 1:
        time.sleep(.1)
except KeyboardInterrupt:
    stopEvent.set()
    t1.join()
    t2.join()
