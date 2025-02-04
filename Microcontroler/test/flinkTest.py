import flink
import time
import threading

stopEvent = threading.Event()

def toggle(gpio: flink.FlinkGPIO):
    pin = 12
    gpio.setDir(pin, True)
    while True:
        gpio.setValue(pin, not gpio.getValue(pin))
        time.sleep(1)
        if (stopEvent.is_set()):
            break

def readFqd(fqd: flink.FlinkFQD):
    ch = 3
    # fqd.reset()
    while True:
        print("FQD: count =", fqd.getCount(ch))
        time.sleep(1)
        if (stopEvent.is_set()):
            break

def outPwm(pwm: flink.FlinkPWM):
    ch = 1
    base = 100000000 #pwm.getBaseClock()
    base = pwm.getBaseClock()
    print("PWM: base clock =", base)
    period = int(base / 1000) 
    highTime = 0
    pwm.setPeriod(ch, period)
    while True:
        pwm.setHighTime(ch, highTime)
        highTime += int(0.05 * period)
        if highTime >= period: highTime = 0
        time.sleep(0.1)
        if (stopEvent.is_set()):
            break

def inPpwa(ppwa: flink.FlinkPPWA, pwm: flink.FlinkPWM):
    ch = 0
    pwm.setPeriod(ch, int(pwm.getBaseClock() * 0.001))    # 1ms
    pwm.setHighTime(ch, int(pwm.getBaseClock() * 0.0002))   # 200us
    base = ppwa.getBaseClock()
    print("PPWA: base clock =", base)
    while True:
        print("PPWA: period =", ppwa.getPeriod(ch) / pwm.getBaseClock(), "s, hightime =", ppwa.getHighTime(ch) / pwm.getBaseClock(), "s")
        time.sleep(1)
        if (stopEvent.is_set()):
            break

def readAdc(adc: flink.FlinkAnalogIn):
    print("adc0 resolution =", adc.getResolution())
    ch = 2
    while True:
        print("ADC0: value =", adc.getValue(ch))
        time.sleep(1)
        if (stopEvent.is_set()):
            break

def readTCRT1000(sense: flink.FlinkReflectiveSensor):
    ch = 0
    while True:
        print("TCRT1000: value =", sense.getValue(ch))
        time.sleep(1)
        if (stopEvent.is_set()):
            break

dev = flink.FlinkDevice()
dev.lsflink()

gpio = flink.FlinkGPIO()
t1 = threading.Thread(target=toggle, args=(gpio,))

fqd = flink.FlinkFQD()
t2 = threading.Thread(target=readFqd, args=(fqd,))

pwm = flink.FlinkPWM()
t3 = threading.Thread(target=outPwm, args=(pwm,))

ppwa = flink.FlinkPPWA()
t4 = threading.Thread(target=inPpwa, args=(ppwa,pwm))

adc = flink.FlinkAnalogIn(flink.FlinkAnalogIn.ADC128S102)
t5 = threading.Thread(target=readAdc, args=(adc,))

tcrt1000 = flink.FlinkReflectiveSensor()
t6 = threading.Thread(target=readTCRT1000, args=(tcrt1000,))

info = flink.FlinkInfo()
print("Info device: total memory size =", hex(info.getMemLength()))
print("Info device: description =", info.getDescription())

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()
try:
    while 1:
        time.sleep(.1)
except KeyboardInterrupt:
    stopEvent.set()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()