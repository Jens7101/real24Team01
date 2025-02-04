import driver
import math
import time

m1 = driver.SignMagnitude(0.01, 2, 3, 3, 64, 5, 3249/196, 0.1, 0.1)
m2 = driver.LockedAntiPhase(0.01, 4, 1, 64, 5, 3249/196, 0.1, 0.1)
speed = 0
diff = 1
try:
    while True:
        print("m1 pos", m1.getPosition(), ", m2 pos", m2.getPosition())
        m1.setSpeed(speed)
        m2.setSpeed(speed)
        if abs(speed) > 3 * math.pi: diff = -diff
        speed += diff
        time.sleep(1)
except KeyboardInterrupt:
    m1.setSpeed(0)
    m2.setSpeed(0)
    time.sleep(0.5) # wait for setpoint to become effective
    m1.exit()
    m2.exit()