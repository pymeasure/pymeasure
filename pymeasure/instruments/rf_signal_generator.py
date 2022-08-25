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
    Of course, in this case, correctness cannot be guaranteed. Some examples are shown below.

Instrument intialization example:

.. code-block:: python

    from pymeasure.instruments.rf_signal_generator import RFSignalGenerator

    sg = RFSignalGenerator('GPIB0::18::INSTR', "Generic Analog RF Signal Generator")
    # Read instrument ID
    sg.id
    # 'Rohde&Schwarz,SMIQ06B,100205/0006,5.80 HX'


Generate a tone at 868MHz:

.. code-block:: python
   
    # Read power
    sg.power
    # -50.0
    # Set power
    sg.power = -60.0
    # Set frequency
    sg.frequency=868000000.0
    # enable RF output
    sg.rf_enable = 1

    
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

    alc = Instrument.control(
        ":SOURCE:POWER:ALC?;", ":SOURCE:POWER:ALC %s;",
        """ A boolean property that enables or disables the automatic leveling control (ALC) circuit.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values={"ON" : 1,
                "OFF" : 0},
        cast = int,
        map_values = True,
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
        super().shutdown()
 
class RFSignalGeneratorDM:
    """ Represent the digital modulation capability of a generic signal generator.

        The digital modulation is the ability to send pattern or user data according to supported modulation.
        Digital data is represented as string so 1 or 0 in transmission order. For non binary modulation, e.g 4FSK, symbols
        are represented as couple of bits.

        This class is a mixin.

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

    """
    
    MODULATION_TYPES = ('ASK', 'BPSK', 'FSK2', 'FSK4', 'PSK8', 'QAM16', 'QAM256', 'QAM32', 'QAM64', 'QPSK')
    """ Define some basic digital modulation types """

    MODULATION_FILTERS = ('RECT', 'GAUS')
    """ Define basic filters """

    MODULATION_DATA = {
        'Pattern0000' : None,
        'Pattern1111' : None,
        'Pattern0101' : None,
        'PatternPN9' : None,
        'DATA' : None,
    }
    """ Define modulation data source, ``DATA`` refers to user bit sequences loaded by :meth:`data_load` and :meth:`data_load_repeated` """


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
        """ Load data into signal generator for transmission.

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

    def set_fsk_constellation(self, constellation, fdev):
        """ For multi level FSK modulation, allow to define the constellation mapping.

        :param constellation: a dictonary which maps to fdev dividers, for an hypothetical 4-FSK example see below.

        :param fdev: Outer frequency deviation

    ``constellation`` parameter example

    .. code-block:: python

        {
            0:   1, # Symbol 00 -> fdev
            1:   3, # Symbol 01 -> fdev/3
            2:  -1, # Symbol 10 -> -fdev
            3:  -3, # Symbol 11 -> -fdev/3
        }
        
        """
        # Subclasses should implement this
        raise Exception ("Not supported/implemented")


class RFSignalGeneratorIQ:
    """ Represent IQ modulation part of a  generic signal generator.

        The IQ modulation to create modulation signal by providing IQ sequences.

        This class define a basic interface which should be implemented for each specific instrument.
        This class is a mixin

An example for data pattern generation

        
.. code-block:: python

    # This example documents the usage of the interface, assuming that is implemented a specific subclass
    # TBD


Another example for user data loading


.. code-block:: python

    # Read instrument ID
    # TBD

    """
    

    memory = None
    """ Memory size for loading user defined patterns """ 

    def _process_iq_sequence(self, sequence):
        """ Identify repetition in sequence and return processed list

        :param sequence: List of string names
        :return : List of items, each item is a list of two elements: name and repetitions

        """
        return_value = []
        repetitions = 0
        for i, name in enumerate(sequence):
            next_name = (sequence + [None])[i+1]
            if (next_name != name):
                return_value.append([name, repetitions+1])
                repetitions = 0
            repetitions += 1

        return return_value

    def _get_iqdata(self, iq_seq):
        """ Utility method that translate iq samples into a list of integers """
        data = []
        iq_data_max_value = 2**(self._iq_data_bits - 1) - 1
        for iq in iq_seq:
            data.append(round(iq.real*iq_data_max_value))
            data.append(round(iq.imag*iq_data_max_value))
        return data

    def data_iq_load(self, iqdata, sampling_rate, name, markers=None):
        """ Load IQ data into signal generator

        IQ data is composed of complex number with magnitude normalized to 1 representing the
        waveform points. Users must provide also the sampling rate to define the playing speed and
        optionally a list of markes for specific relvant points in the waveform.
        Markers are very important to enable function like amplitude calibration and/or provide
        sychronization signals.

        :param iqdata: list I/Q complex samples with magnitude normalized to 1
        :param sampling_rate: IQ data sampling rate in samples per seconds.
        :param name: string defining the name associated with the data.
                     This can be useful to compose sequences.
        :param markers: list of markers items, each marker item is etiher a list of integers
                        (marker dentifier) or integer (representing a bitmask of markers)
                        that are used to mark specific points on a waveform. The length of this
                        list, if different from None, must be equal to length of iqdata list.

        """

        # Subclasses should implement this
        raise Exception ("Not supported/implemented")

    def data_iq_sequence_load(self, iqdata_sequence):
        """ Load IQ sequence into signal generator

        :param iqdata_sequence: list of names representing valid data loaded with :meth:`data_iq_load`
        """
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

    def set_fsk_constellation(self, constellation, fdev):
        """ For multi level FSK modulation, allow to define the constellation mapping.

        :param constellation: a dictonary which maps to fdev dividers, for an hypothetical 4-FSK example see below.

        :param fdev: Outer frequency deviation

    ``constellation`` parameter example

    .. code-block:: python

        {
            0:   1, # Symbol 00 -> fdev
            1:   3, # Symbol 01 -> fdev/3
            2:  -1, # Symbol 10 -> -fdev
            3:  -3, # Symbol 11 -> -fdev/3
        }
        
        """
        # Subclasses should implement this
        raise Exception ("Not supported/implemented")
