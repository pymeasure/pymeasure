from typing import Union
from pint import Quantity as Q_

import pyvisa

from pymeasure.instruments import Instrument, Channel

from pymeasure.instruments.smaract.utils import check_quantity_unit
from pymeasure.instruments.validators import strict_discrete_set


# <channel> : zero-based channel index. Valid indices are 0,1 and 2
# <angel> : the current angle of the position in millidegree


class SCUChannel(Channel):
    unit: str = ''

    frequency_max = Instrument.control(
        ":GCLF{ch}",
        ":SCLF{ch}F%d",
        """Control the maximum frequency in an absolute move""",
        set_process=lambda v: check_quantity_unit(v, 'Hz'),
        get_process=lambda s: Q_(int(s[6:]), 'Hz'),
    )
    safe_direction = Instrument.control(
        ":GSD{ch}",
        ":SSD{ch}D%d",
        """Control the safe direction for a given channel for move_to_ref
           :param  must be either 0 (down) or 1 (up). In minor letters""",
        validator=strict_discrete_set,
        map_values=True,
        values={'up': 1, 'down': 0},
        get_process=lambda x: int(x[-1]),
    )

    def calibrate_sensor(self):
        """Calibrate the sensor. Has to be done before the use of move to reference.
           The user must ensure himself that the positioner is not close to a mechanical
           limit before using this method"""
        self.write(f':CS{self.id}')
        status = self.ask(f":M{self.id}")
        return status

    def set_zero_pos(self):
        """Set the current position as position zero."""
        if self.check_sensor_present():
            self.write(f":SZ{self.id}")
        else:
            raise NotImplementedError

    def set_positioner_type(self, t: int):
        """Set the positioner/sensor type.

           CAUTION! The user has to use the 'SmarAct ASCII Programming Interface' for a
           thorough knowledge of the differnet modes. It ensures the user, that the desired type
           exists, and has the possibility to be implemented to the program.

           The list 'positioner_types' contains the available t values and corresponding properties

        """
        positioner_types = {
            1: "Linear – M",
            4: "Rotary – GC",
            5: "Goniometer – GD",
            6: "Goniometer – GE",
            7: "Rotary – RA",
            8: "Rotary – GF",
            9: "Rotary – RB",
            10: "Rotary – SR36M",
            11: "Rotary – SR36ME",
            12: "Rotary – SR50M",
            13: "Rotary – SR50ME",
            14: "Linear – MM50",
            15: "Goniometer – G935M",
            16: "Linear – MD",
            17: "Tip-Tilt – TT254",
            18: "Linear – LC",
            19: "Rotary – LR",
            20: "Linear – LCD",
            21: "Linear – L",
            22: "Linear – LD",
            23: "Linear – LE",
            24: "Linear – LED",
            25: "Linear – SL…S1I1E1",
            26: "Linear – SL…D1I1E1",
            27: "Linear – SL…S1I2E2",
            28: "Linear – SL…D1I2E2",
            29: "Tip-Tilt – ST…S1I1E2",
            30: "Goniometer – SG…D1L1S",
            31: "Goniometer – SG…D1L1E",
            32: "Goniometer – SG…D1L2S",
            33: "Goniometer – SG…D1L2E",
            34: "Goniometer – SG…D1M1E",
            35: "Goniometer – SG…D1M2E",
            36: "Iris – SI…S1L1S",
            37: "Tip-Tilt – ST…S1I2E2",
            38: "Rotary – SR…T5L3S",
            39: "Iris – SI…S1L4E",
            40: "Iris – SI…S1L1E",
        }
        if t in positioner_types:
            self.write(f":SST{self.id}T{t}")
        else:
            raise ValueError

    def get_positioner_type(self):
        """Get the positioner/sensor type, could be linear or angular"""
        self.write(f":GST{self.id}")
        return self.read()

    def move_steps_up(self, steps: int,
                      freq: Union[int, float, Q_] = None,
                      ampl: Union[int, float, Q_] = None):
        """Moves up
        :param steps: Number of steps, an int in range [1;30000]
        :param freq: Frequency, a quantity given in Hz in range [1;18500] (or int)
        :param ampl: Amplitude, a quantity given in dV in range [150;1000] (or int)
        """

        valid_freq = self.parent.check_freq(freq)
        valid_ampl = self.parent.check_amplitude(ampl)

        f_val = int(valid_freq.to('Hz').magnitude)
        a_val = int(valid_ampl.to('dV').magnitude)

        self.write(f":U{self.id}F{f_val}A{a_val}S{steps}")
        # self._current_steps += steps

    def move_steps_down(self, steps: int,
                        freq: Union[int, float, Q_] = None,
                        ampl: Union[int, float, Q_] = None):
        """Moves down
        :param steps: Number of steps, an int in range [1;30000]
        :param freq: Frequency, a quantity given in Hz in range [1;18500] (or int)
        :param ampl: Amplitude, a quantity given in dV in range [150;1000] (or int)
        """
        #
        valid_freq = self.parent.check_freq(freq)
        valid_ampl = self.parent.check_amplitude(ampl)

        f_val = int(valid_freq.to('Hz').magnitude)
        a_val = int(valid_ampl.to('dV').magnitude)

        self.write(f":D{self.id}F{f_val}A{a_val}S{steps}")
        # self._current_steps -= steps

    def check_sensor_present(self) -> bool:
        """Check if the sensor is present

        :returns: True/False

        """
        self.write(f':GSP{self.id}')
        response = self.read()
        return response == f':SP{self.id}P'

    def move_to_ref(self):
        """Moves up/down to reference"""
        self.write(f":MTR{self.id}H0Z1")
        self._current_steps = 0

    def move_to_end_up(self):
        """Moves up until end of line"""
        self.write(f":MES{self.id}DU")
        self._current_steps = -20000

    def move_to_end_down(self):
        """Moves down until end of line"""
        self.write(f":MES{self.id}DD")
        self._current_steps = 20000

    def stop(self):
        """Stops any process."""
        self.write(f":S{self.id}")

    def get_position(self):
        """Returns the current position in pint qunatity measured in micrometers."""
        raise NotImplementedError


class SCUChannelLinear(SCUChannel):
    unit = 'µm'

    def move_abs(self, position: Q_):
        self.write(f":MPA{self.id}P{check_quantity_unit(position, self.unit)}")

    def get_position(self):
        """Returns the current position in micrometers."""
        self.write(f":GP{self.id}")
        pos = self.read()
        self.position = Q_(float(pos[4:]), self.unit)
        return self.position

    def move_rel(self, position: Q_):
        """Moves up a distance + current position"""
        self.write(f":MPR{self.id}P{check_quantity_unit(position, self.unit)}")


class SCUChannelAngular(SCUChannel):
    unit = 'm°'

    def move_abs(self, position: Q_):
        """Moves to the absolute angle given in m° from the reference position via
           closed-loop control.

           :param angle: A quantity with angular units (m°)
        """
        self.write(f":MAA{self.id}P{check_quantity_unit(position, self.unit)}")

    def get_angle(self):
        """ Returns the current angle in degrees"""
        self.write(f":GA{self.id}")
        ang = self.read()
        self.angle = (Q_(float(ang[4:]), self.unit))
        return self.angle

    def move_rel(self, position: Q_):
        """Moves the relative angle given in m° from the current position closed-loop control.

           :param angle: A quantity with angular units (m°)
        """
        self.write(f":MAR{self.id}A{check_quantity_unit(position, self.unit)}")


class SCUChannelStepper(SCUChannel):
    """
    Channel for an open-loop positioner without a sensor.
    All positions are estimated by counting steps.
    """
    unit = 'step'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_steps = 0

    def get_position_step(self):
        """ Returns the current estimated position in steps. """
        # We simply read our internal counter variable
        return self._current_steps

    def move_rel(self, steps: Union[int, Q_]):
        """Moves to the relative position given in steps from the current possition

        :param steps : A quantity with the step as unit, given as integer,
                       with positive int = down, negative int = up.
        """
        old_steps = self._current_steps
        if isinstance(steps, Q_):
            steps_val = int(steps.magnitude)
        else:
            steps_val = int(steps)

        if steps_val > 0:
            self.move_steps_up(steps_val)
            self._current_steps = steps_val + old_steps
        elif steps_val < 0:
            self.move_steps_down(abs(steps_val))
            self._current_steps = steps_val + old_steps



    def move_abs(self, position: Union[int, Q_]):
        """Moves to the absolute position given in steps from the reference possition

        :param steps : A quantity with the step as unit, given as integer
        """
        if isinstance(position, Q_):
            target_steps = int(position.magnitude)
        else:
            target_steps = int(position)

        diff = target_steps - self._current_steps

        # We use our own move_rel function to do the actual work
        self.move_rel(diff)


class SmarActSCU_ASCII(Instrument):
    """
    Communication with a SmarAct SCU (Simple Control Unit) motion controller via ASCII.

    The SmarAct SCU product line includes one- and three-channel control systems
    for driving piezo stages, with optional support for closed-loop
    positioning using position or angle sensors.

    SCU controllers communicate via USB or RS232. Program uses a simple ASCII command
    protocol, which is implemented by this driver.

    This base class provides the common communication layer and shared
    functionality, while axis-specific behavior (e.g. linear or angular motion)
    is implemented in subclasses.

    :param str adapter: Name of the COM-port.
    :param int timeout: Timeout in ms.
    """

    channel0 = Instrument.ChannelCreator(SCUChannel, "0")
    channel1 = Instrument.ChannelCreator(SCUChannel, "1")
    channel2 = Instrument.ChannelCreator(SCUChannel, "2")

    def __init__(self, adapter, name='SCUController',
                 includeSCPI=False, **kwargs):
        super().__init__(adapter, name, includeSCPI=False,
                         read_termination='\n',
                         write_termination='\n',
                         **kwargs)

        self._amplitude: Q_ = Q_(400, 'dV')
        self._freq: Q_ = Q_(3000, 'Hz')
        self._steps: int = 2000
        self._current_steps: int = 0

    def close(self):
        self.adapter.close()

    serial_nb = Instrument.measurement(
        ":GID", """Get the serial number. """,
        get_process=lambda s: s[3:]
    )

    model = Instrument.measurement(
        ":I", """Get the device model information. """,
        get_process=lambda s: s[2:]
    )

    # CHECK AMPLITUDE
    def check_amplitude(self, ampl: Union[int, str, Q_] = None) -> Q_:
        """Check if amplitude is present and if it is inside the given boundary.

               :param ampl : a quantity with amplitude units dV, if int then given in dV
               """
        if ampl is None:
            return self._amplitude

        if isinstance(ampl, int):
            ampl = Q_(ampl, 'dV')

        if isinstance(ampl, str):
            ampl = Q_(ampl)

        if not (Q_(150, 'dV') <= ampl <= Q_(1000, 'dV')):
            raise ValueError(f"Amplitude {ampl} out of range [150; 1000] dV")
        return ampl

    @property
    def amplitude(self):
        """ Control default frequency """
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value: Union[int, Q_]):
        self._amplitude = self.check_amplitude(value)

    # CHECK FREQUENCY

    def check_freq(self, freq: Union[int, str, Q_] = None) -> Q_:
        """ Check if closed-loop frequency is present and if it is inside the given boundary.

        :param freq: a qunatity with frequency units in Hz, if int, then given in Hz
        """
        if freq is None:
            return self._freq

        if isinstance(freq, int):
            freq = Q_(freq, 'Hz')

        if isinstance(freq, str):
            freq = Q_(freq)

        # Vérification of limits
        if not (Q_(1, 'Hz') <= freq <= Q_(18500, 'Hz')):
            raise ValueError(f"Frequency {freq} out of range [1; 18500] Hz")

        return freq

    @property
    def frequency(self):
        """ Control default frequency """
        return self._freq

    @frequency.setter
    def frequency(self, value: Union[int, Q_]):
        self._freq = self.check_freq(value)

    # CHECK STEPS

    def check_steps(self, steps: int):
        """Check if steps are present and if it is inside the given boundary."""
        if steps is None:
            steps = self._steps
        else:
            self._steps = steps
        if not (1 <= steps <= 30000):
            raise ValueError('Steps out of the range [1;30000] steps (int) ')
        return steps

    # MOVEMENT

    def move_abs(self, position: Union[Q_, int]):
        """Moves to the absolute position given in µm from the reference possition

        :param position : A quantity with length units (µm), if integer, then given in µm
        """
        raise NotImplementedError

    def move_rel(self, position: Q_):
        """Moves the relative distance given in µm from current position

        :param position : A quantity with length units (µm)
        """
        if position.magnitude >= 0:
            self.move_steps_up(position.magnitude)
        else:
            self.move_steps_down(position.magnitude)

    BAUDRATE = (9600, 38400, 57600, 100000, 115200,
                128000, 256000, 500000)

    def set_baudrate(self, baudrate: int):
        """Set the baudrate AND reset the instrument. Reseting is necessary to update the baudrate.

        param baudrate : Currently supported baudrates are: 9600, 38400, 57600, 100000,
                         115200, 128000, 256000, 500000.
        """
        if baudrate in self.BAUDRATE:
            self.write(f':CB{baudrate}')
            self.write(':R')
        else:
            raise pyvisa.VisaIOError(-1)

    def reset(self):
        """Reset will be performed on the device. Has the same effect
           as a power-down/power-up cycle
        """
        self.write(':R')


class SmarActSCULinear(SmarActSCU_ASCII):

    channel0 = Instrument.ChannelCreator(SCUChannelLinear, "0")
    channel1 = Instrument.ChannelCreator(SCUChannelLinear, "1")
    channel2 = Instrument.ChannelCreator(SCUChannelLinear, "2")


class SmarActSCUAngular(SmarActSCU_ASCII):

    channel0 = Instrument.ChannelCreator(SCUChannelAngular, "0")
    channel1 = Instrument.ChannelCreator(SCUChannelAngular, "1")
    channel2 = Instrument.ChannelCreator(SCUChannelAngular, "2")


class SmarActSCUStepper(SmarActSCU_ASCII):
    channel0 = Instrument.ChannelCreator(SCUChannelStepper, "0")
    channel1 = Instrument.ChannelCreator(SCUChannelStepper, "1")
    channel2 = Instrument.ChannelCreator(SCUChannelStepper, "2")


if __name__ == "__main__":
    inst = SmarActSCUStepper('ASRL3::INSTR')
    #inst.baudrate = 9600
    pass

    # import pyvisa
    # rm = pyvisa.ResourceManager()
    # ressources = rm.list_resources()
    # print(ressources)
    #
    # inst = rm.open_resource(ressources[0])
    # inst.write_termination = '\n'
    # inst.read_termination = '\n'
    # pass
    #
    inst.close()
