import driver
import time
xadc = driver.XADC()

def RawtoVoltage(value):
    return (value/4096)

while True:
    print("CH0: ", end="")
    print(xadc.read(0))
    print("CH1: ", end="")
    print(xadc.read(1))
    print("CH2: ", end="")
    print(xadc.read(2))
    print("CH3: ", end="")
    print(xadc.read(3))
    time.sleep(1)


