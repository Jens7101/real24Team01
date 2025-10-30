import flink
import time


MotLeftFor = 0
MotLeftBack = 1
MotRightFor = 2
MotRightBack = 3
pwmFreq=20000
pwm=flink.FlinkPWM()
period=int(pwm.getBaseClock()/pwmFreq)
pwm.setPeriod(MotLeftFor,period)
pwm.setPeriod(MotLeftBack,period)
pwm.setPeriod(MotRightFor,period)
pwm.setPeriod(MotRightBack,period)


gpio = flink.FlinkGPIO()
Programmstart = 10
Start = 11
Back = 12
Stop = 13
Set = 14
gpio.setDir(Start, False)
gpio.setDir(Set, False)
gpio.setDir(Back, False)
gpio.setDir(Stop, False)
gpio.setDir(Programmstart, False)


while gpio.getValue(Programmstart) == True:
    time.sleep(0.1)
    if gpio.getValue(Start) == True:
        MotSpeedLeftFor = int(period/4)
        MotSpeedLeftBack = 0
        MotSpeedRightFor = int(period/4)
        MotSpeedRightBack = 0

    if gpio.getValue(Back) == True:
        MotSpeedLeftFor = 0
        MotSpeedLeftBack = int(period/4)
        MotSpeedRightFor = 0
        MotSpeedRightBack = int(period/4)    
    
    if gpio.getValue(Stop) == True:
        MotSpeedLeftFor = 0
        MotSpeedLeftBack = 0
        MotSpeedRightFor = 0
        MotSpeedRightBack = 0

    if gpio.getValue(Set) == True:
        pwm.setHighTime(MotLeftFor,MotSpeedLeftFor)
        pwm.setHighTime(MotLeftBack,MotSpeedLeftBack)
        pwm.setHighTime(MotRightFor,MotSpeedRightFor)
        pwm.setHighTime(MotRightBack,MotSpeedRightBack)

print("Programm beendet")







