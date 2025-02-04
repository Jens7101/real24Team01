import flink
import threading
import time

stopEvent = threading.Event()

def writer(uart0: flink.FlinkUART, uart1: flink.FlinkUART):
    byte = ord('A')
    while not stopEvent.is_set():
        uart0.write(byte)
        uart1.write(byte)
        byte += 1
        if (byte > ord('z')): 
            byte = ord('A')
        time.sleep(1)

def reader(uart0: flink.FlinkUART, uart1: flink.FlinkUART):
    while not stopEvent.is_set():
        if uart0.availToRead() > 0:
            print("read from uart0", chr(uart0.read()))
        if uart1.availToRead() > 0:
            print("read from uart1", chr(uart1.read()))

uart0 = flink.FlinkUART(0)
uart1 = flink.FlinkUART(1)
uart0.reset()
uart0.start(115200)
uart1.start(115200)

t1 = threading.Thread(target=writer, args=(uart0,uart1))
t1.start()
t2 = threading.Thread(target=reader, args=(uart0,uart1))
t2.start()

try:
    while 1:
        time.sleep(.1)
except KeyboardInterrupt:
    stopEvent.set()
    t1.join()
    t2.join()
