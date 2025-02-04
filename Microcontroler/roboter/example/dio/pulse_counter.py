import flink
import time

LED1 = 5
SCHALTER= 3


gpio = flink.FlinkGPIO()
gpio.setDir(LED1, True)
gpio.setValue(LED1, False)
gpio.setDir(SCHALTER, False)
schaltstellungOld =not gpio.getValue(SCHALTER)
counter = 0
while True:
    schaltstellung = gpio.getValue(SCHALTER)
    if schaltstellung != schaltstellungOld:
        counter += 1
        print(counter)
        schaltstellungOld = schaltstellung
        time.sleep(1.0)


