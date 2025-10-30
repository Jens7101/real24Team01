import flink

 
chnL = 1
chnR = 0
pwmFreq=20000
pwm=flink.FlinkPWM()
period=int(pwm.getBaseClock()/pwmFreq)
pwm.setPeriod(chnL,period)
pwm.setPeriod(chnR,period)

#leftfull
#currHightimeL=period
#currHightimeR=0

#lefthalf
currHightimeL=int(period/2)
currHightimeR=0

#rightfull
#currHightimeL=0
#currHightimeR=period

#righthalf
#currHightimeL=0
#currHightimeR=int(period/2)

#stop
#currHightimeL=0
#currHightimeR=0

pwm.setHighTime(chnL,currHightimeL)
pwm.setHighTime(chnR,currHightimeR)




