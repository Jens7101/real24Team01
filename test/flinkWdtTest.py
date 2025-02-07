import flink
import time
import threading

stopEvent = threading.Event()
sleepTime = 0.05

def runIt(wdt: flink.FlinkWDT):
    clk = wdt.getBaseClock()
    wdt.setCounter(int(10 * clk))
    wdt.arm()
    while True:
        wdt.setCounter(int(0.1 * clk))
        time.sleep(sleepTime)
        if (stopEvent.is_set()):
            break

wdt = flink.FlinkWDT()
t1 = threading.Thread(target=runIt, args=(wdt,))
startTime = time.time()
t1.start()
once = False
try:
    while 1:
        if time.time() > startTime + 10 and not once: 
            print("enlarge sleep time, should runout soon")
            sleepTime = 0.2
            once = True
        print("wdt status =", hex(wdt.getStatus()))
        time.sleep(1)
except KeyboardInterrupt:
    stopEvent.set()
    t1.join()
