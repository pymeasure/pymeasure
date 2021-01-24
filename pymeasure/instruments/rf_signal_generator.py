#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, strict_range, joined_validators

# Capitalize string arguments to allow for better conformity with other WFG's
def capitalize_string(string: str, *args, **kwargs):
    return string.upper()

# Combine the capitalize function and validator
string_validator = joined_validators(capitalize_string, strict_discrete_set)


class RFSignalGenerator(Instrument):
    """Represents a generic analog RF Signal Generator.

    It provides a high-level interface for interacting with the instrument and all the instrument inherited from
    this class should have the same base interface plus optionally device specific extensions.
    The class is not normally intended to be used directly but should be subclassed to implement support for specific instruments.
    For RF signal generators not yet supported, this class can also be used to provide initial basic functions.
    Of course, in this case, correctness cannot be guaranteed.

    Initialization of the Instrument
    ====================================

.. code-block:: python

    from pymeasure.instruments.rf_signal_generator import RFSignalGenerator

    sg = RFSignalGenerator('GPIB0::18::INSTR', "Generic Analog RF Signal Generator")
    # Read instrument ID
    sg.id
    # 'Rohde&Schwarz,SMIQ06B,100205/0006,5.80 HX'


Generate a tone at 868MHz
====================================================

.. code-block:: python
   
    # Read power
    sg.power
    # -50.0
    # Set power
    a.power = -60.0
    # Set frequency
    sg.frequency=868000000.0
    # enable RF output
    a.rf_enable = 1

    
    """

    POWER_RANGE_dBm = (-150.0, 30.0)

    FREQUENCY_RANGE_Hz = (1, 100e9)

    power = Instrument.control(
        ":POW?;", ":POW %g dBm;",
        """ A floating point property that represents the output power
        in dBm. This property can be set.
        """,
        validator=strict_range,
        values=POWER_RANGE_dBm,
        dynamic=True
    )
    frequency = Instrument.control(
        ":FREQ?;", ":FREQ %e Hz;",
        """ A floating point property that represents the output frequency
        in Hz. This property can be set.
        """,
        validator=strict_range,
        values=FREQUENCY_RANGE_Hz,
        dynamic=True
    )
    rf_enable = Instrument.control(
        ":OUTPUT?", ":OUTPUT %d", 
        """ A boolean property that tell if RF output is enabled or not. 
        This property can be set. """,
        cast=int,
        dynamic=True
    )

    def __init__(self, adapter, description, **kwargs):
        super().__init__(
            adapter, description, **kwargs
        )


    def shutdown(self):
        """ Shuts down the instrument by disabling any modulation
        and the output signal.
        """
        self.rf_enable = 0
 
    def check_errors(self):
        """Return any accumulated errors.
        """
        retVal = []
        while True:
            error = self.ask("SYSTEM:ERROR?")
            f = error.split(",")
            errorCode = int(f[0])
            if errorCode == 0:
                break
            else:
                retVal.append(error)
        return retVal
        
class RFSignalGeneratorDM(RFSignalGenerator):
    """ Represent a generic signal generator with digital modulation capability.

        The digital modulation is the ability to send pattern or user data according to supported modulation.
        Digital data is represented as string so 1 or 0 in transmission order. For non binary modulation, e.g 4FSK, symbols
        are represented as couple of bits.

        This class define a basic interface which should be implemented for each specific instrument.

An example for data pattern generation

        
.. code-block:: python

    # This example documents the usage of the interface, assuming that is implemented a specific subclass
    from pymeasure.instruments.agilent.agilentE4438C import AgilentE4438C

    sg = AgilentE4438C('GPIB0::18::INSTR')
    # Read instrument ID
    sg.id
    # Agilent Technologies, E4438C, MY45094883, C.05.85
    sg.custom_modulation_data = "Pattern0101"
    sg.custom_modulation = "2FSK"
    sg.custom_modulation_symbol_rate = 38400
    sg.custom_modulation_fsk_deviation = 20000

    sg.custom_modulation_enable = 1
    sg.rf_enable = 1
    sg.shutdown()


Another example for user data loading


.. code-block:: python

    sg = AgilentE4438C('GPIB0::18::INSTR')
    # Read instrument ID
    sg.id
    # Agilent Technologies, E4438C, MY45094883, C.05.85
    sg.custom_modulation = "FSK2"
    sg.custom_modulation_symbol_rate = 38400
    sg.custom_modulation_fsk_deviation = 20000
    sg.data_load_repeated("10101010" + "100010001000" + "0001101100000011001", 50, 10)
    sg.custom_modulation_data = "DATA"
    sg.custom_modulation_enable = 1
    sg.rf_enable = 1
    sg.data_trigger_setup()
    sg.data_trigger()
    sg.shutdown()

    """
    
    MODULATION_TYPES = ('BPSK', 'FSK2', 'FSK4', 'PSK8', 'QAM16', 'QAM256', 'QAM32', 'QAM64', 'QPSK')
    """ Define some basic digital modulation types """

    MODULATION_FILTERS = ('RECT', 'GAUS')
    """ Define basic filters """

    MODULATION_DATA = {
        'Pattern0011' : None,
        'Pattern0101' : None,
        'PatternPN9' : None,
        'DATA' : None,
    }
    """ Define modulation data source, DATA refer to user bit sequences loaded by :meth: data_load and :meth: data_load_repeated """


    custom_modulation_data  = None
    """ Instrument control or setting to implement setting of the modulation data source """

    custom_modulation_enable = None
    """ Instrument control to enable (writing 1)/disable(writing 0) the digital modulation """

    custom_modulation = None
    """ Instrument property that allow to select the modulation """

    custom_modulation_filter = None
    """ Instrument control to select the modulation filter """

    custom_modulation_bbt = None
    """ property representing the bandwidth-symbol time product for filters """

    custom_modulation_symbol_rate = None
    """ property representing the symbol rate in symbols/sec """

    custom_modulation_fsk_deviation = None
    """ frequency deviation parameters for FSK modulations """

    custom_modulation_ask_depth = None
    """ ASK depth in percentage """

    memory = None
    """ Memory size for loading user defined patterns """ 

    def data_load_repeated(self, bitsequence, spacing, repetitions):
        """ Load digital data into signal generator for transmission, the parameters are:
        :param bitsequence: string of '1' or '0' in transmission order
        :param spacing: integer, gap between repetition expressed in number of bit
        :param repetitions: integer, how many times the bit sequence is repeated
        """
        self.data_load((bitsequence,)*repetitions, (spacing,)*repetitions)

    def data_load(self, bitsequences, spacings):
        """ Load data into signal generator for transmission, the parameters are:
        :param bitsequences: items list. Each item is a string of '1' or '0' in transmission order
        :param spacings: integer list, gap to be inserted between each bitsequence  expressed in number of bit
        """
        # Subclasses should implement this
        raise Exception ("Not supported/implemented")

    def data_trigger_setup(self, mode='SINGLE'):
        """ Configure the trigger system for bitsequence transmission
        """
        # Subclasses should implement this
        raise Exception ("Not supported/implemented")

    def data_trigger(self):
        """ Trigger a bitsequence transmission
        """
        # Subclasses should implement this
        raise Exception ("Not supported/implemented")
