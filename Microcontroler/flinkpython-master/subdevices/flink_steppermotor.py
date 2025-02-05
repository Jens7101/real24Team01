import flink
import ctypes as ct
from enum import Enum
import math

__author__  = "Patrick Good, Urs Graf"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class FlinkStepperMotor(flink.FlinkSubDevice):
    """
    The flinksteppermotor subdevice realizes an reflectiv sensor within a flink device.
    Each Channel generates an IRQ when the motor has stopped
    """

    class LocalConfReg(Enum):
        """
        Bit definitions for the local configuration register.
        """
        DIRECTION   = 0         # Motor direction
        STEP_MODE   = 1         # Step mode
        PHASE_MODE  = 2         # Phase mode
        RUN_MODE_0  = 3         # Operating mode bit 0
        RUN_MODE_1  = 4         # Operating mode bit 1
        START       = 5         # Motor start
        RESET_STEPS = 6         # Reset step count

    class RunMode(Enum):
        """
        Motor operation modes.
        """
        DISABLED    = 0         # Motor is disabled (no holding torque)
        STEPPING    = 1         # Stepping mode (Motor takes a fixed number of steps)
        FIXED_SPEED = 2         # Fixed speed mode (Motor moves at a constant speed)
        RESERVED    = 3         # Not implemented, yet. Throws an Exception

    class Direction(Enum):
        """
        Motor direction definitions.
        """
        CLOCKWISE         = 1   # Clockwise direction
        COUNTER_CLOCKWISE = 0   # Counter-clockwise direction

    class StepMode(Enum):
        """
        Motor stepping mode definitions.
        """
        FULL_STEPS = 1         # Full-step mode
        HALF_STEPS = 0         # Half-step mode

    class PhaseMode(Enum):
        """
        Motor phase mode definitions.
        Has an effect only in full step mode
        """
        TWO_PHASE = 1          # Two-phase mode
        ONE_PHASE = 0          # One-phase mode

    def __init__(self):
        """
        Creates a stepper motor object.
        
        Parameters
        ----------
        
        Returns
        -------
        the object
        """
        dev = flink.FlinkDevice()
        subDev = dev.getSubdeviceByType(flink.Definitions.STEPPER_MOTOR_INTERFACE_ID)
        super().__init__(dev, subDev)
        dev.lib.flink_stepperMotor_get_baseclock.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_stepperMotor_get_baseclock.restype = ct.c_int

        dev.lib.flink_stepperMotor_set_local_config_reg.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_stepperMotor_set_local_config_reg.restype = ct.c_int  
        dev.lib.flink_stepperMotor_get_local_config_reg.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_stepperMotor_get_local_config_reg.restype = ct.c_int
        dev.lib.flink_stepperMotor_set_local_config_reg_bits_atomic.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_stepperMotor_set_local_config_reg_bits_atomic.restype = ct.c_int
        dev.lib.flink_stepperMotor_reset_local_config_reg_bits_atomic.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_stepperMotor_reset_local_config_reg_bits_atomic.restype = ct.c_int

        dev.lib.flink_stepperMotor_set_prescaler_start.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_stepperMotor_set_prescaler_start.restype = ct.c_int
        dev.lib.flink_stepperMotor_get_prescaler_start.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_stepperMotor_get_prescaler_start.restype = ct.c_int
        dev.lib.flink_stepperMotor_set_prescaler_top.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_stepperMotor_set_prescaler_top.restype = ct.c_int
        dev.lib.flink_stepperMotor_get_prescaler_top.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_stepperMotor_get_prescaler_top.restype = ct.c_int
        
        dev.lib.flink_stepperMotor_set_acceleration.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_stepperMotor_set_acceleration.restype = ct.c_int
        dev.lib.flink_stepperMotor_get_acceleration.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_stepperMotor_get_acceleration.restype = ct.c_int

        dev.lib.flink_stepperMotor_set_steps_to_do.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32]
        dev.lib.flink_stepperMotor_set_steps_to_do.restype = ct.c_int
        dev.lib.flink_stepperMotor_get_steps_to_do.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_stepperMotor_get_steps_to_do.restype = ct.c_int
        dev.lib.flink_stepperMotor_get_steps_have_done.argtypes = [ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]
        dev.lib.flink_stepperMotor_get_steps_have_done.restype = ct.c_int

        dev.lib.flink_steppermotor_global_step_reset.argtypes = [ct.c_void_p]
        dev.lib.flink_steppermotor_global_step_reset.restype = ct.c_int

        self._BASE_CLOCK = self._getBaseclock()

    ##################################################################################
    # Internal methodes
    ##################################################################################
    def _setStartSpeed(self, channel: int, prescaler: int) -> None:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Writes the start speed for the motor.
        This describes the duration of the first step.

        A change is only taken into account when the motor has stopped.
        
        Parameters
        ----------
        channel   : channel number
        prescaler : prescaler based on base clock
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_stepperMotor_set_prescaler_start(self.subDev, channel, prescaler)
        if error < 0:
            raise flink.FlinkException(f"Failed set the presacaler start value: {prescaler} on channel: {channel}", error, self.subDev)

    def _setSollSpeed(self, channel: int, prescaler: int) -> None:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Writes the soll speed for the motor.
        This describes the duration of a soll speed step.

        In "fixed speed" mode it can be changed at any time, but in "stepping" 
        mode a change is only taken into account when the motor has stopped.
        
        Parameters
        ----------
        channel   : channel number
        prescaler : prescaler based on base clock
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_stepperMotor_set_prescaler_top(self.subDev, channel, prescaler)
        if error < 0:
            raise flink.FlinkException(f"Failed set the presacaler soll value: {prescaler} on channel: {channel}", error, self.subDev)

    def _setAcceleration(self, channel: int, acceleration: int) -> None:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Writes the acceleration of the motor between start and target speed.

        In "fixed speed" mode it can be changed at any time, but in "stepping" 
        mode a change is only taken into account when the motor has stopped.
        
        Parameters
        ----------
        channel      : channel number
        acceleration : prescaler based on base clock
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_stepperMotor_set_acceleration(self.subDev, channel, acceleration)
        if error < 0:
            raise flink.FlinkException("Failed set acceleration value: 0x{0:x} on channel: {1}".format(acceleration, channel), error, self.subDev)
    
    def _getBaseclock(self) -> int:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Returns the base clock of the underlying hardware.
        
        Returns
        -------
        The base clock in Hz
        """
        clock = ct.c_uint32()
        error = self.dev.lib.flink_stepperMotor_get_baseclock(self.subDev, clock)
        if error < 0:
            raise flink.FlinkException("Failed to read the base clock", error, self.subDev)
        return int(clock.value)
    
    def _calculatePrescaler(self, speed: float) -> int:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Parameters
        ----------
        speed : [steps/s]
        
        Returns
        -------
        prescaler value based on the base clock
        """
        if speed <= 0:
            raise flink.FlinkException("Speed cannot be negative", None, self.subDev)
        prescaler: int = int(self._BASE_CLOCK/speed)
        return prescaler if prescaler > 0 else 1
    
    def _calculateSpeed(self, prescaler: int) -> float:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Parameters
        ----------
        prescaler value based on the base clock
        
        Returns
        -------
        speed [steps/s]
        """
        if prescaler <= 0: 
            raise flink.FlinkException("Invalied prescaler value", None, self.subDev)
        return float(self._BASE_CLOCK)/float(prescaler)
    
    def _calculateStepsFromAcceleration(self, prescaler_start: int, prescaler_soll: int, acceleration: int) -> float:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Parameters
        ----------
        prescaler_start : prescaler start value based on the base clock
        prescaler_soll  : prescaler soll value based on the base clock
        acceleration    : raw acceleration
        
        Returns
        -------
        Steps to do between start and stop speed
        """
        if prescaler_start < 1 or prescaler_soll < 1 or acceleration < 1:
            raise flink.FlinkException("Failed to calculate steps from acceleration", None, self.subDev)
        return math.ceil((float(prescaler_start - prescaler_soll))/acceleration)
    
    def _calculateAccelerationFromSteps(self, prescaler_start: int, prescaler_soll: int, steps: int) -> float:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Parameters
        ----------
        prescaler_start : prescaler start value based on the base clock
        prescaler_soll  : prescaler soll value based on the base clock
        steps           : steps to do between start ans soll
        
        Returns
        -------
        Acceleration as number of steps between start and stop speed
        """
        if prescaler_start < 1 or prescaler_soll < 1 or steps < 1:
            raise flink.FlinkException("Failed to calculate acceleration from steps", None, self.subDev)
        return math.ceil((float(prescaler_start - prescaler_soll))/steps)
    
    def _getStartPrescaler(self, channel: int) -> int:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Reads the start speed for the motor.
        This describes the duration of the first step.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Motor start prescaler
        """
        prescaler = ct.c_uint32()
        error = self.dev.lib.flink_stepperMotor_get_prescaler_start(self.subDev, channel, prescaler)
        if error < 0:
            raise flink.FlinkException(f"Failed to read start prescaler on channel: {channel}", error, self.subDev)
        return int(prescaler.value)
    
    def _getSollPrescaler(self, channel: int) -> int:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Reads the soll speed for the motor.
        This describes the duration of a soll speed step.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Motor soll speed prescaler
        """
        prescaler = ct.c_uint32()
        error = self.dev.lib.flink_stepperMotor_get_prescaler_top(self.subDev, channel, prescaler)
        if error < 0:
            raise flink.FlinkException(f"Failed to read top prescaler on channel: {channel}", error, self.subDev)
        return int(prescaler.value)
    
    def _getAcceleration(self, channel: int) -> int:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Reads the acceleration of the motor between start and target speed.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        acceleration raw
        """
        acc = ct.c_uint32()
        error = self.dev.lib.flink_stepperMotor_get_acceleration(self.subDev, channel, acc)
        if error < 0:
            raise flink.FlinkException(f"Failed to read top prescaler on channel: {channel}", error, self.subDev)
        return int(acc.value)
    
    def _setTwoBits(self, channel: int, numberToSet: int, maskBit_0: int, maskBit_1: int) -> None:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--
        
        Parameters
        ----------
        channel     : channel number
        numberToSet : Number which have to be set
        maskBit_0   : Place to (re)set the first bit from the number
        maskBit_1   : Place to (re)set the second bit from the number
        
        Returns
        -------
        None
        """
        if numberToSet == 0:
            error_0 = self.dev.lib.flink_stepperMotor_reset_local_config_reg_bits_atomic(self.subDev, channel, maskBit_0 | maskBit_1)
            error_1 = 0
        elif numberToSet == 1:
            error_0 = self.dev.lib.flink_stepperMotor_set_local_config_reg_bits_atomic(self.subDev, channel, maskBit_0)
            error_1 = self.dev.lib.flink_stepperMotor_reset_local_config_reg_bits_atomic(self.subDev, channel, maskBit_1)
        elif numberToSet == 2:
            error_0 = self.dev.lib.flink_stepperMotor_reset_local_config_reg_bits_atomic(self.subDev, channel, maskBit_0)
            error_1 = self.dev.lib.flink_stepperMotor_set_local_config_reg_bits_atomic(self.subDev, channel, maskBit_1)
        elif numberToSet == 3:
            error_0 = self.dev.lib.flink_stepperMotor_set_local_config_reg_bits_atomic(self.subDev, channel, maskBit_0 | maskBit_1)
            error_1 = 0
        else:
            raise flink.FlinkException(f"Number: {numberToSet} must be 0 <= number < 4.", None, self.subDev)

        if error_0 < 0 or error_1 < 0:
            error = error_0 if error_0 < 0 else error_1
            mask = maskBit_0 | maskBit_1
            raise flink.FlinkException(f"Failed to (re)set two bits at mask: {mask} on channel: {channel}", error, self.subDev)
        
    def _setBit(self, channel: int, setBit: int, maskBit: int) -> None:
        """
        --> Internal method. NOT recomended to use this function directly!!! <--

        Reads the acceleration of the motor between start and target speed.
        
        Parameters
        ----------
        channel : channel number
        setBit  : 0 reset the bit, 1 set the bit
        maskBit : Place to (re)set the bit
        
        Returns
        -------
        None
        """
        if setBit == 0:
            error = self.dev.lib.flink_stepperMotor_reset_local_config_reg_bits_atomic(self.subDev, channel, maskBit)
        elif setBit == 1:
            error = self.dev.lib.flink_stepperMotor_set_local_config_reg_bits_atomic(self.subDev, channel, maskBit)
        else:
            raise flink.FlinkException(f"Bit: {setBit} must be 0 <= number < 1.", None, self.subDev)
        if error < 0:
            raise flink.FlinkException(f"Failed to (re)set bit at mask: {maskBit} on channel: {channel}", error, self.subDev)


    ##################################################################################
    # External methodes
    ##################################################################################
    def initMotor(self,
                  channel: int,
                  runMode: RunMode,
                  startSpeed : float,
                  sollSpeed: float,
                  acc_steps: float,
                  steppsToDo: int = 0,
                  direction: Direction = Direction.CLOCKWISE,
                  stepMode: StepMode = StepMode.FULL_STEPS,
                  phaseMode: PhaseMode = PhaseMode.TWO_PHASE) -> None:
        """
        This method initzialises the motor.

        It is recommended to use this method when using the motor for the first time or when changing the running mode.

        Do not use it while the motor is running. It throw an exception.

        Parameters
        ----------
        channel      : channel number
        runMode      : The mode in which the engine must run. Use the defines in the class "RunMode".
        startSpeed   : Motor start speed [steps/s]
        sollSpeed    : Motor soll speed [steps/s]
        acceleration : Acceleration between start and soll speed [nof steps]
        steppsToDo   : Steps to do
        direction    : clockwise or counter clockwise. Use the defines in the class "Direction"
        stepMode     : Full or half steps. Use the defines in the class "StepMode"
        phaseMode    : Two oder one phase. Use the defines in the class "PhaseMode"

        Returns
        -------
        None

        Raises
        ------
        test
        """
        if self.isMotorRunning(channel=channel):
            raise flink.FlinkException("It's not allowed to initialise the motor while it's running.", None, self.subDev)

        pre_start = self._calculatePrescaler(speed=startSpeed)
        pre_soll = self._calculatePrescaler(speed=sollSpeed) 
        acc_raw = self._calculateAccelerationFromSteps(prescaler_start=pre_start, prescaler_soll=pre_soll, steps=acc_steps)
        self.setRunMode(channel=channel, runMode=runMode)
        self._setStartSpeed(channel=channel, prescaler=pre_start)
        self._setSollSpeed(channel=channel, prescaler=pre_soll)
        self._setAcceleration(channel=channel, acceleration=acc_raw)
        self.setStepsToDo(channel=channel, stepps=steppsToDo)
        self.setDirection(channel=channel, direction=direction)
        self.setStepMode(channel=channel, stepMode=stepMode)
        self.setPhaseMode(channel=channel, phaseMode=phaseMode)

    def changeSollSpeedWhileRunning(self, channel: int, sollSpeed: int, acceleration: int) -> None:
        """
        To change the soll speed while motor is running. It will also adjust the acceleration.

        Do not use it while the motor is stopped. It throw an exception.

        Parameters
        ----------
        channel      : channel number
        sollSpeed    : Motor soll speed [steps/s]
        acceleration : Acceleration between start and soll speed [nof steps]

        Returns
        -------
        None
        """
        if not self.isMotorRunning(channel=channel):
            raise flink.FlinkException("It's not allowed to change speed of the motor while it's stopped.", None, self.subDev)

        pre_soll = self._calculatePrescaler(speed=sollSpeed)
        pre_start = self._getStartPrescaler(channel=channel)
        acc_raw = self._calculateAccelerationFromSteps(prescaler_soll=pre_soll, prescaler_start=pre_start, steps=acceleration)
        self._setAcceleration(channel=channel, acceleration=acc_raw) # do not change the order
        self._setSollSpeed(channel=channel, prescaler=pre_soll)

    def updateSpeeds(self, channel: int, startSpeed: int, sollSpeed: int, acceleration: int) -> None:
        """
        To change the different speeds if the motor is stopped.

        Do not use it while the motor is running. It throw an exception.

        Parameters
        ----------
        channel      : channel number
        startSpeed   : Motor start speed [steps/s]
        sollSpeed    : Motor soll speed [steps/s]
        acceleration : Acceleration between start and soll speed [nof steps]
        
        Returns
        -------
        None
        """
        if self.isMotorRunning(channel=channel):
            raise flink.FlinkException("It's not allowed to update speeds of the motor while it's running.", None, self.subDev)

        pre_start = self._calculatePrescaler(speed=startSpeed)
        pre_soll = self._calculatePrescaler(speed=sollSpeed)
        acc_raw = self._calculateAccelerationFromSteps(prescaler_soll=pre_soll, prescaler_start=pre_start, steps=acceleration)
        self._setStartSpeed(channel=channel, prescaler=pre_start)
        self._setSollSpeed(channel=channel, prescaler=pre_soll)
        self._setAcceleration(channel=channel, acceleration=acc_raw)

    def getBaseclock(self) -> int:
        """
        Returns the base clock of the underlying hardware.
        
        Returns
        -------
        The base clock in Hz
        """
        return self._BASE_CLOCK

    def unsave_setLocalConfiguration(self, channel: int, config: int) -> None:
        """
        Writes the local configuration per channel.
        
        Unsave because if a bit should change its a "read modify write" operation (not atomic).
        Use "setBitsInLocalConfiguration" or "resetBitsInLocalConfiguration" instead or the 
        provided function to change a mode.
                
        Parameters
        ----------
        channel : channel number
        config  : the configuration for the channel
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_stepperMotor_set_local_config_reg(self.subDev, channel, config)
        if error < 0:
            raise flink.FlinkException(f"Failed to write the local config: {config} on channel: {channel}", error, self.subDev)
    
    def getLocalConfiguration(self, channel: int) -> int:
        """
        Reads the local configuration
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        the configuration for the channel
        """
        config = ct.c_uint32()
        error = self.dev.lib.flink_stepperMotor_get_local_config_reg(self.subDev, channel, config)
        if error < 0:
            raise flink.FlinkException(f"Failed to read the local config: {config} on channel: {channel}", error, self.subDev)
        return int(config.value)

    def setBitsInLocalConfiguration(self, channel: int, bitsToSet: int) -> None:
        """
        Sets the corresponding bits in the local configuration (atomic).
        A zero has no effect.

        Example:
        bitsToSet:           00101001
        local conf reg:      01001011 "or" operation
                             --------
        local conf reg new:  01101011
        
        Parameters
        ----------
        channel   : channel number
        bitsToSet : Which bits need to be set in the local configuration
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_stepperMotor_set_local_config_reg_bits_atomic(self.subDev, channel, bitsToSet)
        if error < 0:
            raise flink.FlinkException(f"Failed to set bits: {bitsToSet} on channel: {channel}", error, self.subDev)

    def resetBitsInLocalConfiguration(self, channel: int, bitsToReset: int) -> None:
        """
        Resets the corresponding bits in the local configuration (atomic).
        A zero has no effect.
        
        Example:
        bitsToSet:           00101001 
        local conf reg:      01001011 "nand" operation
                             --------
        local conf reg new:  01000010

        Parameters
        ----------
        channel : channel number
        bitsToSet : Which bits need to be reset in the local configuration
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_stepperMotor_reset_local_config_reg_bits_atomic(self.subDev, channel, bitsToReset)
        if error < 0:
            raise flink.FlinkException(f"Failed to reset bits: {bitsToReset} on channel: {channel}", error, self.subDev)
        
    def getStartSpeed(self, channel: int) -> int:
        """
        Reads the start speed for the motor.
        This describes the duration of the first step.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Motor start speed [steps/s]
        """
        prescaler = self._getStartPrescaler(channel)
        try:
            return self._calculateSpeed(prescaler)
        except flink.FlinkException:
            raise flink.FlinkException(f"Failed calculate start speed of channel: {channel}", channel, self.subDev)
    
    def getSollSpeed(self, channel: int) -> int:
        """
        Reads the soll speed for the motor.
        This describes the duration of a soll speed step.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Motor soll speed [steps/s]
        """
        prescaler = self._getSollPrescaler(channel)
        try:
            return self._calculateSpeed(prescaler)
        except flink.FlinkException:
            raise flink.FlinkException(f"Failed calculate top speed of channel: {channel}", channel, self.subDev)
    
    def getAcceleration(self, channel: int) -> int:
        """
        Reads the acceleration of the motor between start and target speed.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Acceleration as number of steps between start and stop speed
        """
        pre_start = self._getStartPrescaler(channel)
        pre_soll = self._getSollPrescaler(channel)
        acc = self._getAcceleration(channel)
        try:
            return self._calculateStepsFromAcceleration(prescaler_start = pre_start, prescaler_soll = pre_soll, acceleration = acc)
        except flink.FlinkException:
            raise flink.FlinkException(f"Failed calculate acceleration of channel: {channel}", channel, self.subDev)

    def setStepsToDo(self, channel: int, stepps: int) -> None:
        """
        Writes the steps to be performed in "stepping" mode.

        A change is only taken into account when the motor has stopped.

        No effect in "fixed speed" mode.
        
        Parameters
        ----------
        channel : channel number
        steps   : Steps to do
        
        Returns
        -------
        None
        """
        error = self.dev.lib.flink_stepperMotor_set_steps_to_do(self.subDev, channel, stepps)
        if error < 0:
            raise flink.FlinkException(f"Failed to write stepps: {stepps} on channel: {channel}", error, self.subDev)
    
    def getStepsToDo(self, channel: int) -> int:
        """
        Reads the steps to be performed in "stepping" mode.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Steps to do
        """
        stepps = ct.c_uint32()
        error = self.dev.lib.flink_stepperMotor_get_steps_to_do(self.subDev, channel, stepps)
        if error < 0:
            raise flink.FlinkException(f"Failed to read stepps to do on channel: {channel}", error, self.subDev)
        return int(stepps.value)

    def getStepsHaveDone(self, channel: int) -> int:
        """
        Reads the steps taken by the motor since the last reset.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Steps have dome
        """
        stepps = ct.c_uint32()
        error = self.dev.lib.flink_stepperMotor_get_steps_have_done(self.subDev, channel, stepps)
        if error < 0:
            raise flink.FlinkException(f"Failed to read stepps have done on channel: {channel}", error, self.subDev)
        return int(stepps.value)
    
    def resetStepsGlobal(self) -> None:
        """
        Resets all stepcounter (steps have done) on all channels.
        
        Parameters
        ----------
        
        Returns
        -------
        None        
        """
        error = self.dev.lib.flink_steppermotor_global_step_reset(self.subDev)
        if error < 0:
            raise flink.FlinkException("Failed to reset stepps have done global", error, self.subDev)

    def resetStepsLocal(self, channel: int) -> None:
        """
        Resets the stepcounter (steps have done) from the channels.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        None
        """
        mask = ct.c_uint32(1<<self.LocalConfReg.RESET_STEPS.value)
        error = self.dev.lib.flink_stepperMotor_set_local_config_reg_bits_atomic(self.subDev, channel, mask)
        if error < 0:
            raise flink.FlinkException(f"Failed to reset stepps have done on channel: {channel}", error, self.subDev)

    def setDirection(self, channel: int, direction: Direction) -> None:
        """
        Writes the direction of the motor.

        A change is only taken into account when the motor has stopped.
        
        Parameters
        ----------
        channel   : channel number
        direction : clockwise or counter clockwise. Use the defines in the class "Direction"
        
        Returns
        -------
        None
        """
        mask = ct.c_uint32(1<<self.LocalConfReg.DIRECTION.value)
        if direction == self.Direction.CLOCKWISE:
            self._setBit(channel=channel, setBit=self.Direction.CLOCKWISE.value, maskBit=mask)
        else:
            self._setBit(channel=channel, setBit=self.Direction.COUNTER_CLOCKWISE.value, maskBit=mask)

    def getDirection(self, channel: int) -> Direction:
        """
        Reads the direction of the motor.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Direction
        """
        mask = 1<<self.LocalConfReg.DIRECTION.value
        confReg = self.getLocalConfiguration(channel)
        if (((confReg & mask) >> self.LocalConfReg.DIRECTION.value) == self.Direction.CLOCKWISE.value):
            return self.Direction.CLOCKWISE
        else: 
            return self.Direction.COUNTER_CLOCKWISE

    def setStepMode(self, channel: int, stepMode: StepMode) -> None:
        """
        Writes the step mode of the motor.

        A change is only taken into account when the motor has stopped.
        
        Parameters
        ----------
        channel  : channel number
        stepMode : Full or half steps. Use the defines in the class "StepMode"
        
        Returns
        -------
        None
        """
        mask = ct.c_uint32(1<<self.LocalConfReg.STEP_MODE.value)
        if stepMode == self.StepMode.FULL_STEPS:
            self._setBit(channel=channel, setBit=self.StepMode.FULL_STEPS.value, maskBit=mask)
        else:
            self._setBit(channel=channel, setBit=self.StepMode.HALF_STEPS.value, maskBit=mask)

    def getStepMode(self, channel: int) -> StepMode:
        """
        Reads the step mode of the motor.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Step mode
        """
        mask = 1<<self.LocalConfReg.STEP_MODE.value
        confReg = self.getLocalConfiguration(channel)
        if (((confReg & mask) >> self.LocalConfReg.STEP_MODE.value) == self.StepMode.FULL_STEPS.value):
            return self.StepMode.FULL_STEPS
        else: 
            return self.StepMode.HALF_STEPS

    def setPhaseMode(self, channel: int, phaseMode: PhaseMode) -> None:
        """
        Writes the phase mode of the motor.

        A change is only taken into account when the motor has stopped.

        Parameters
        ----------
        channel   : channel number
        phaseMode : Two oder one phase. Use the defines in the class "PhaseMode"
        
        Returns
        -------
        Phase mode
        """
        mask = ct.c_uint32(1<<self.LocalConfReg.PHASE_MODE.value)
        if phaseMode == self.PhaseMode.ONE_PHASE:
            self._setBit(channel=channel, setBit=self.PhaseMode.ONE_PHASE.value, maskBit=mask)
        else:
            self._setBit(channel=channel, setBit=self.PhaseMode.TWO_PHASE.value, maskBit=mask)

    def getPhaseMode(self, channel: int) -> PhaseMode:
        """
        Reads the phase mode of the motor.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Phase Mode
        """
        mask = 1<<self.LocalConfReg.PHASE_MODE.value
        confReg = self.getLocalConfiguration(channel)
        if (((confReg & mask) >> self.LocalConfReg.PHASE_MODE.value) == self.PhaseMode.ONE_PHASE.value):
            return self.PhaseMode.ONE_PHASE
        else: 
            return self.PhaseMode.TWO_PHASE

    def setRunMode(self, channel: int, runMode: RunMode) -> None:
        """
        Writes the run mode of the motor.

        It's not recomended to change while the motor is running
        
        Parameters
        ----------
        channel : channel number
        runMode : The mode in which the engine must run. Use the defines in the class "RunMode".
        
        Returns
        -------
        None
        """
        maskRunBit_0 = 1<<self.LocalConfReg.RUN_MODE_0.value
        maskRunBit_1 = 1<<self.LocalConfReg.RUN_MODE_1.value
        
        # Case distinction
        if runMode == self.RunMode.DISABLED:
            self._setTwoBits(channel = channel, numberToSet = self.RunMode.DISABLED.value, maskBit_0 = maskRunBit_0, maskBit_1 = maskRunBit_1)
        elif runMode == self.RunMode.STEPPING:
            self._setTwoBits(channel = channel, numberToSet = self.RunMode.STEPPING.value, maskBit_0 = maskRunBit_0, maskBit_1 = maskRunBit_1)
        elif runMode == self.RunMode.FIXED_SPEED:
            self._setTwoBits(channel = channel, numberToSet = self.RunMode.FIXED_SPEED.value, maskBit_0 = maskRunBit_0, maskBit_1 = maskRunBit_1)
        else:
            raise flink.FlinkException(f"This mode: {runMode.name} is reserved. DO NOT USE IT!!!", -1, self.subDev)

    def getRunMode(self, channel: int) -> RunMode:
        """
        Reads the run mode of the motor.
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        Run Mode
        """
        confReg = self.getLocalConfiguration(channel)
        mask = 1<<self.LocalConfReg.RUN_MODE_0.value | 1<<self.LocalConfReg.RUN_MODE_1.value
        config = (confReg & mask) >> self.LocalConfReg.RUN_MODE_0.value
        if config == self.RunMode.DISABLED.value:
            return self.RunMode.DISABLED
        elif config == self.RunMode.STEPPING.value:
            return self.RunMode.STEPPING
        elif config == self.RunMode.FIXED_SPEED.value:
            return self.RunMode.FIXED_SPEED
        else:
            return self.RunMode.RESERVED

    def start(self, channel: int) -> None:
        """
        Starts the Motor
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        None
        """
        mask = ct.c_uint32(1<<self.LocalConfReg.START.value)
        error = self.dev.lib.flink_stepperMotor_set_local_config_reg_bits_atomic(self.subDev, channel, mask)
        if error < 0:
            raise flink.FlinkException(f"Failed to start motor on channel: {channel}", error, self.subDev)

    def stop(self, channel: int, acceleration: float = None) -> None:
        """
        Stops the Motor
        
        A change to acceleration is only allowed in "Fixed Speed" mode

        Parameters
        ----------
        channel : channel number
        acceleration : Number of steps to stop the motor
        
        Returns
        -------
        None
        """
        mode = self.getRunMode(channel=channel)

        if acceleration != None and mode == self.RunMode.FIXED_SPEED:
            pre_start = self._getStartPrescaler(channel=channel)
            pre_soll = self._getSollPrescaler(channel=channel)
            acc_raw = self._calculateAccelerationFromSteps(prescaler_start=pre_start, prescaler_soll=pre_soll, steps=acceleration)
            self._setAcceleration(channel=channel, acceleration=acc_raw)

        mask = ct.c_uint32(1<<self.LocalConfReg.START.value)
        error = self.dev.lib.flink_stepperMotor_reset_local_config_reg_bits_atomic(self.subDev, channel, mask)
        if error < 0:
            raise flink.FlinkException(f"Failed to stop motor on channel: {channel}", error, self.subDev)
        
    def isMotorRunning(self, channel: int) -> bool:
        """
        Checks if the motor is running or not
        
        Parameters
        ----------
        channel : channel number
        
        Returns
        -------
        True if running else False
        """
        mask = 1<<self.LocalConfReg.START.value
        confReg = self.getLocalConfiguration(channel)

        if ((confReg & mask) >> self.LocalConfReg.START.value):
            return True
        else: 
            return False