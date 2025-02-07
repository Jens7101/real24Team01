import flink
import time

testChannel = 0
pwmFreq = 20000

pwm = flink.FlinkPWM()
period = pwm.getBaseClock() / pwmFreq
pwm.setPeriod(testChannel, int(period))
pwm.setHighTime(testChannel, int(period * 0.2))

highTime = 0
counter = 0
while True:
    counter = 0
    while counter <= 5:
        highTime = (highTime + period / 10) % period
        pwm.setHighTime(testChannel, int(highTime))
        counter += .5
        time.sleep(.5)