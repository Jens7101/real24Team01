import flink
import time

LED1 = 5 

gpio = flink.FlinkGPIO()
gpio.setDir(LED1, True)
gpio.setValue(LED1, False)

while True:
        gpio.setValue(LED1, True)
        time.sleep(1)
        gpio.setValue(LED1, False)
        time.sleep(2)

