import flink
import time

LED1 = 5
SCHALTER= 3


gpio = flink.FlinkGPIO()
gpio.setDir(LED1, True)
gpio.setValue(LED1, False)
gpio.setDir(SCHALTER, False)
while True:
    schaltstellung = gpio.getValue(SCHALTER)
    gpio.setValue(LED1, schaltstellung)
    time.sleep(1.0)