import flink
import threading
import time
import math

__author__ = "Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class Control:
    """
    Base class for speed controller (PI control) for DC motor.
    This controller can work with two pwm channels operating in sign-magnitude mode or
    it can work with one pwm channel operating in locked-antiphase mode.

    The motor and the encoder have to be connected carefully. A positive speed control must lead to a positive speed reading.
    If this is not the case you have to change either the connections to the motor or the signals of the encoder (but not both!). 
    """
  
    def __init__(self, ts: float, encChannel: int, encTPR: int, umax: float, i: float, kp: float, tn: float):
        """
        Create a new speed controller for a DC motor. 
        Do not use the constructor of this base class directly.
        """
        self.fqd = flink.FlinkFQD()
        self.pwm = flink.FlinkPWM()
        self.scale = (float)((2 * math.pi) / (encTPR * 4 * i)) # scaling factor [rad/tick], factor 4 for fast quadrature decoding
        self.b0 = kp * (1 + ts / (2 * tn))  # controller coefficients
        self.b1 = kp * (ts / (2 * tn) - 1)  # controller coefficients
        self.ts = ts  # [s]
        self.encChannel = encChannel
        self.umax = umax    # [V]
        self.absPos = 0 # [ticks]
        self.speed = 0 # [1/s]
        self.pwmFreq = 20000 # frequency of the pwm control signal in Hz
        self.period = int(self.pwm.getBaseClock() / self.pwmFreq)
        self.desSpeed = 0   # desired speed
        self.fqd.reset()    # initialize FQD channels
        self.exitEvent = threading.Event()

    def _run(self) -> None:
        """
        Controller run method. This method will be periodically called.
        """
        self.prevTime = time.time()
        self.prevPos = self.fqd.getCount(self.encChannel)
        self.prevControlValue = 0
        self.e_1 = 0
        # count = 0
        while(True):
            if (self.exitEvent.is_set()): break
        
            t1 = time.time()
            dt = (t1 - self.prevTime)
            self.prevTime = t1

            actPos = self.fqd.getCount(self.encChannel)
            deltaPos = actPos - self.prevPos
            self.prevPos = actPos
            self.absPos += deltaPos
            self.speed = (deltaPos * self.scale) / dt
            
            e = self.desSpeed - self.speed
            controlValue = self.prevControlValue + self.b0 * e + self.b1 * self.e_1
            
            # anti windup
            if controlValue > self.umax: controlValue = self.umax
            if controlValue < -self.umax: controlValue = -self.umax
            
            self._setPWMDuty(controlValue / self.umax)	# update PWM
            self.e_1 = e
            self.prevControlValue = controlValue

            # if count % 100 == 0: 
            #     print(f'd1={dt:.4f}, deltaPos={deltaPos}, speed={self.speed:.4f}, act={actPos}, prev={bla}, controlValue={controlValue:.4f}')
            # count += 1

            time.sleep(self.ts)

    def setSpeed(self, speed: float) -> None:
        """
        Set desired speed.
        
        Parameters
        ----------
        speed : desired speed in radian per second [1/s] 

        Returns
        -------
        None
        """
        self.desSpeed = speed

    def getSpeed(self) -> float:
        """
        Returns the current speed.
        
        Returns
        -------
        current speed in radian per second [1/s]
        """
        return self.speed

    def getPosition(self) -> float:
        """
        Returns the current absolute position.
        
        Returns
        -------
        absolute position in radian
        """
        return self.absPos * self.scale

    def setPWMFreq(self, freq: float) -> None:
        """
        Set desired PWM frequency. Default is 20000Hz.
        
        Parameters
        ----------
        freq : frequency of the pwm control signal in Hz 

        Returns
        -------
        None
        """
        self.period = int(self.pwm.getBaseClock() / freq)

    def exit(self) -> None:
        """
        Stops the thread running this controller.
        
        Returns
        -------
        None
        """
        self.exitEvent.set()

    def _setPWMDuty(self, dutyCycle: float) -> None:
        pass

class SignMagnitude(Control):
    """
    Speed controller (PI control) for DC motor.
    This controller works with two pwm channels operating in sign-magnitude mode.

    The motor and the encoder have to be connected carefully. A positive speed control must lead to a positive speed reading.
    If this is not the case you have to change either the connections to the motor or the signals of the encoder (but not both!). 
    """

    def __init__(self, ts: float, pwmChannel1: int, pwmChannel2: int, encChannel: int, encTPR: int, umax: float, i: float, kp: float, tn: float):
        """
        Create a new speed controller for a DC motor. The controller works in sign-magnitude mode using two PWM signals. 
        
        Parameters
        ----------
        ts : task period in seconds [s]
	    pwmChannel1 : channel for the first PWM signal
        pwmChannel2 : channel for the second PWM signal
        encChannel : channel for the encoder signal. Connect both A and B to the associated pins
        encTPR : impulse/ticks per rotation of the encoder
        umax : maximum output voltage of set value
        i : gear transmission ratio
        kp : controller gain factor. For experimental evaluating the controller parameters, begin with kp = 1
        tn : time constant of the controller. For experimental evaluating the controller parameters, set tn to the mechanical time constant of your axis. If the motor has a gear it's assumed that the torque of inertia of the rotor is dominant. 
             That means you can set tn equals to the mechanical time constant of your motor. 
        """
        super().__init__(ts, encChannel, encTPR, umax, i, kp, tn)
        self.pwmChannel0 = pwmChannel1
        self.pwmChannel1 = pwmChannel2
        # initialize PWM channels
        self.pwm.setPeriod(pwmChannel1, self.period)
        self.pwm.setPeriod(pwmChannel2, self.period)
        self.pwm.setHighTime(pwmChannel1, 0)
        self.pwm.setHighTime(pwmChannel2, 0)
        t = threading.Thread(target=self._run)
        t.start()

    def _setPWMDuty(self, dutyCycle: float) -> None:
        if dutyCycle >= 0:   # forward
            self.pwm.setHighTime(self.pwmChannel0, 0)   # direction, set to 0
        else:   # backward
            self.pwm.setHighTime(self.pwmChannel0, self.period) # direction, set to 1
            dutyCycle = dutyCycle + 1
        self.pwm.setHighTime(self.pwmChannel1, int(dutyCycle * self.period))   # speed

class LockedAntiPhase(Control):
    """
    Speed controller (PI control) for DC motor.
    This controller works with one pwm channel operating in locked anti-phase mode.

    The motor and the encoder have to be connected carefully. A positive speed control must lead to a positive speed reading.
    If this is not the case you have to change either the connections to the motor or the signals of the encoder (but not both!). 
    """

    def __init__(self, ts: float, pwmChannel: int, encChannel: int, encTPR: int, umax: float, i: float, kp: float, tn: float):
        """
        Create a new speed controller for a DC motor. The controller works in locked anti-phase mode using one PWM signal. 
        
        Parameters
        ----------
        ts : task period in seconds [s]
	    pwmChannel : channel for the PWM signal
        encChannel : channel for the encoder signal. Connect both A and B to the associated pins
        encTPR : impulse/ticks per rotation of the encoder
        umax : maximum output voltage of set value
        i : gear transmission ratio
        kp : controller gain factor. For experimental evaluating the controller parameters, begin with kp = 1
        tn : time constant of the controller. For experimental evaluating the controller parameters, set tn to the mechanical time constant of your axis. If the motor has a gear it's assumed that the torque of inertia of the rotor is dominant. 
             That means you can set tn equals to the mechanical time constant of your motor. 
        """
        super().__init__(ts, encChannel, encTPR, umax, i, kp, tn)
        self.pwmChannel = pwmChannel
        # initialize PWM channel
        self.pwm.setPeriod(pwmChannel, self.period)
        self.pwm.setHighTime(pwmChannel, 0)
        t = threading.Thread(target=self._run)
        t.start()

    def _setPWMDuty(self, dutyCycle: float) -> None:
        self.pwm.setHighTime(self.pwmChannel, int((dutyCycle + 1) / 2 * self.period))   # direction, set to 0

