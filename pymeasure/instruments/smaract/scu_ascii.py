from typing import Union
from pint import Quantity as Q_

from pymeasure.instruments import Instrument, Channel

from pymeasure.instruments.smaract.utils import check_quantity_unit
from pymeasure.instruments.validators import truncated_discrete_set, strict_discrete_set


# <channel> : zero-based channel index. Valid indices are 0,1 and 2
# <angel> : the current angle of the position in millidegree

class SCUChannel(Channel):

    unit: str = ''

    frequency_max = Instrument.control(
        ":GCLF{ch}",
        ":SCLF{ch}F%d",
        """Control the maximum frequency in an absolute move""",
        set_process = lambda v: check_quantity_unit(v, 'Hz'),
        get_process = lambda s: Q_(s[6:], 'Hz'),
    )
    safe_direction = Instrument.control(
        ":GSD{ch}",
        ":SSD{ch}D%d",
        """Control the safe direction for a given channel for move_to_ref
           :param  must be either 0 (down) or 1 (up). In minor letters""",
        validator=strict_discrete_set,
        map_values=True,
        values = {'up':1,'down':0},
        get_process=lambda x: int(x[-1]),
    )

    def calibrate_sensor(self):
        """Calibrate the sensor. Has to done before the use of move to reference.
           The user must ensure himself that the positioner is not close to a mechanical limit"""
        self.write(f':CS{self.id}')
        status = self.ask(f":M{self.id}")

    def set_zero_pos(self):
        """Set the current position as position zero."""
        if self.check_sensor_present():
            self.write(f":SZ{self.id}")
        else:
            raise NotImplementedError

    def set_positioner_type(self, t: int):
        """Set the positioner/sensor type.

           CAUTION! The user has to use the 'SmarAct ASCII Programming Interface' for a thorough knowledge of the differnet modes
           It will ensure the user, that the desired type exists, and has the possibility to be implemented
           to the program.

           The list ''positioner_types' contains the available t values and corresponding properties

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
        #else:
        #    raise NotImplementedError

    def get_positioner_type(self):
        """Get the positioner/sensor type, could be linear or angular"""
        self.write(f":GST{self.id}")
        return self.read()

    def move_steps_up(self, steps: int, freq: Q_ = None, ampl: Q_ = None):
        """Moves up

        :param steps: Number of steps, an int in range [1;30000]
        :param freq: Frequency, a quantity given in Hz in range [1;18500]
        :param ampl: Amplitude, a quantity given in dV in range [150;1000]

        """
        if freq is None:
            freq = self._freq
        if ampl is None:
            ampl = self._amplitude
        self.write(f":U{self.id}F{freq.to('Hz').magnitude}A{ampl.to('dV').magnitude}S{steps}")

    def move_steps_down(self, steps: int, freq: Q_ = None, ampl: Q_ = None):
        """Moves down

        :param steps: Number of steps, an int in range [1;30000]
        :param freq: Frequency, a quantity given in Hz in range [1;18500]
        :param ampl: Amplitude, a quantity given in dV in range [150;1000]

        """
        if freq is None:
            freq = self._freq
        if ampl is None:
            ampl = self._amplitude
        self.write(f":D{self.id}F{freq.to('Hz').magnitude}A{ampl.to('dV').magnitude}S{steps}")

    def check_sensor_present(self) -> bool:
        """Check if the sensor is present

        :returns: True/False

        """
        self.write(f':GSP{self.id}')
        response = self.read()
        return response == f':SP{self.id}P'

    def move_to_ref(self):
        """Moves up/down to reference"""
        if self.unit == '':
            raise NotImplementedError
        else:
            self.write(f":MTR{self.id}H0Z1")
            status = self.ask(f":M{self.id}")
            print(status)

    def move_to_end_up(self):
        """Moves up until end of line"""
        self.write(f":MES{self.id}DU")

    def move_to_end_down(self):
        """Moves down until end of line"""
        self.write(f":MES{self.id}DD")

    def stop(self):
        """Stops any process."""
        self.write(f":S{self.id}")
        status = self.ask(f":M{self.id}")
        print(status)

    def get_position(self) :
        """Returns the current position in micrometres."""
        #if check_sensor_present():
        if self.unit == '':
            raise NotImplementedError


class SCUChannelLinear(SCUChannel):
    unit = 'µm'

    def move_abs(self, position: Q_):
        self.write(f":MPA{self.id}P{check_quantity_unit(position, self.unit)}")

    def get_position(self):
        """Returns the current position in micrometers."""
        self.write(f":GP{self.id}")
        pos = self.read()
        self.position = (Q_(float(pos[4:]), self.unit))
        return self.position

    def move_rel(self, position: Q_):
        """Moves up a distance + current position"""
        self.write(f":MPR{self.id}P{check_quantity_unit(position, self.unit)}")

class SCUChannelAngular(SCUChannel):
    unit = 'm°'

    def move_abs(self, position: Q_):
        """Moves to the absolute angle given in m° from the reference position via closed-loop control.

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
    :param str address: ---.
    :param int timeout: Timeout in ms.
    """
    #ici je me suis basé sur le tc038, qui est souvent utilisé dans le manuel de PyMeasure

    channel0 = Instrument.ChannelCreator(SCUChannel, "0")
    channel1 = Instrument.ChannelCreator(SCUChannel, "1")
    channel2 = Instrument.ChannelCreator(SCUChannel, "2")

    def __init__(self, adapter, name='SCUController', **kwargs):
        super().__init__(adapter, name,
                         read_termination='\n',
                         write_termination='\n',
                         **kwargs)

        self._amplitude: Q_ = Q_(300, 'dV')
        self._freq: Q_ = Q_(260, 'Hz')
        self._steps: int = 250
        #self._safe_direction: str = safe_direction

    identif = Instrument.measurement(
        ":GID", """Get the identification number. """

    )

    model = Instrument.measurement(
        ":I", """Get the device identification information. """
    )

    ###CHECK AMPLITUDE###

    def check_amplitude(self, ampl: Union[int, str, Q_] = None) -> Q_:
        """Check if amplitude is present and if it is inside the given boundary.

        :param ampl : a quantity with amplitude units dV, if int then given in dV
        """
        if ampl is None:
            ampl = self.amplitude
        else:
            ampl = check_quantity_unit(ampl, 'dV')
        if not (150 <= ampl.magnitude <= 1000):
            raise ValueError("Amplitude out of range [150;1000] dV'")
        return ampl

    @property
    def amplitude(self):
        """ Get/set default frequency """
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value: Union[int, Q_]):
        self._amplitude = self.check_amplitude(value)

    ###CHECK FREQUENCY###

    def check_freq(self, freq: Union[int, str, Q_] = None) -> Q_:
        """Check if frequency is present and if it is inside the given boundary.

        :param freq: a qunatity with frequency units in Hz, if int, then given in Hz
        """
        if freq is None:
            freq = self.frequency
        else:
            freq = check_quantity_unit(freq, 'Hz')
        if not (Q_(1, 'Hz') < freq < self.frequency_max):
            raise ValueError('Frequency ut of the range [1;18500] Herz')
        return freq

    @property
    def frequency(self):
        """ Get/set default frequency """
        return self._freq

    @frequency.setter
    def frequency(self, value: Union[int, Q_]):
        self._freq = self.check_freq(value)

    def check_steps(self, steps: int):
        """Check if steps are present and if it is inside the given boundary."""
        if steps is None:
            steps = self._steps
        else:
            self._steps = steps
        if not (1 <= steps <= 30000):
            raise ValueError('Steps out of the range [1;30000] steps (int) ')
        return steps

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

    def set_baudrate(self, baudrate :int):
        """Set the baudrate after the next reset done

        param baudrate : Currently supported baud rates are: 9600, 38400, 57600, 100000, 115200, 128000, 256000, 500000.
        """
        self.write(f':CB(baudrate)')
        #return self.read()
        #propietes
    def reset(self):
        """Reset will be performed on the device. Has the same effect as a power-down/power-up cycle"""
        self.write(f':R(reset)')

class SmarActSCULinear(SmarActSCU_ASCII):
    unit = 'um'

    channel0 = Instrument.ChannelCreator(SCUChannelLinear, "0")
    channel1 = Instrument.ChannelCreator(SCUChannelLinear, "1")
    channel2 = Instrument.ChannelCreator(SCUChannelLinear, "2")

class SmarActSCUAngular(SmarActSCU_ASCII):

    channel0 = Instrument.ChannelCreator(SCUChannelAngular, "0")
    channel1 = Instrument.ChannelCreator(SCUChannelAngular, "1")
    channel2 = Instrument.ChannelCreator(SCUChannelAngular, "2")

if __name__ == "__main__":
    inst = SmarActSCULinear('ASRL3::INSTR')
    pass

    #import pyvisa
    # rm = pyvisa.ResourceManager()
    #ressources = rm.list_resources()
    #print(ressources)
    #
    # inst = rm.open_resource(ressources[0])
    # inst.write_termination = '\n'
    # inst.read_termination = '\n'
    # pass
    #
    inst.close()
