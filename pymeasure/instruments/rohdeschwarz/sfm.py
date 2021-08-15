#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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


import logging
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())



class SFM(Instrument):
    """ Represents the Rohde&Schwarz SFM TV test transmitter
    interface for interacting with the instrument.

    """

    def __init__(self, resourceName, **kwargs):
        super(SFM, self).__init__(
            resourceName,
            "Rohde&Schwarz SFM",
            includeSCPI = True,
            **kwargs
        )

    def calibration(self,number=1,subsystem=None):
        """
        Function to either calibrate the whole modulator, when subsystem paramtrer is omitted,
        or calibrate a subsystem of the modulator.

        Valid subssyem selections: "NICam, VISion, SOUNd1|2, CODer"

        """
        if subsystem is None:
            self.write("CAL:MOD%d" % (number))
        else:
            self.write("CAL:MOD%d:%s" % (number,strict_discrete_set(subsystem,
                                        ["NIC","VIS","SOUN1","SOUN2","COD"])))

    #INST (Manual 3.6.4)
    system_number = Instrument.control(
        "INST:SEL ?",
        "INST:SEL: SYS%d",
        """A int property for the selected systems (if more then 1 available)

        * Minimum 1
        * Maximum 6

        """,
        validator = strict_range,
        values = [1, 6],
        check_set_errors=True,
        )

    #ROUTE (Manual 3.6.5)
    R75_out = Instrument.control(
        "ROUT:CHAN:OUTP:IMP?",
        "ROUT:CHAN:OUTP:IMP %s",
        """ A bool property that controls the use of the 75R output (if installed)

        ======  =======
        Value   Meaning
        ======  =======
        False   50R output active (N)
        True    75R output active (BNC)
        ======  =======
        """,
        validator = strict_discrete_set,
        values={False:"LOW", True:"HIGH"},
        map_values = True,
        )

    ext_ref_basic = Instrument.control(
        "ROUT:REF:CLOCK:BAS?",
        "ROUT:REF:CLOCK:BAS %s",
        """ A bool property for the external reference for the basic unit

        ======  =======
        Value   Meaning
        ======  =======
        False   Internal 10 MHz is used
        True    External 10 MHz is used
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:"INT", True:"EXT"},
        map_values = True,
        )

    ext_ref_extenstion = Instrument.control(
        "ROUT:REF:CLOCK:EXT?",
        "ROUT:REF:CLOCK:EXT %s",
        """ A bool property for the external reference for the extension frame

        ======  =======
        Value   Meaning
        ======  =======
        False   Internal 10 MHz is used
        True    External 10 MHz is used
        ======  =======
        """,
        validator = strict_discrete_set,
        values={False:"INT", True:"EXT"},
        map_values = True,
        )

    ext_vid_connector = Instrument.control(
        "ROUT:TEL:VID:EXT?",
        "ROUT:TEL:VID:EXT %s",
        """A string property controlling which connector is used as the input of the video source

        Possible selections are:

        ======  =======
        Value   Meaning
        ======  =======
        HIGH    Front connector - Hi-Z
        LOW     Front connector - 75R
        REAR1   Rear connector 1
        REAR2   Rear connector 2
        AUTO    Automatic assignment
        ======  =======
        """,
        validator = strict_discrete_set,
        values = ["HIGH","LOW","REAR1","REAR2","AUTO"],
        )

    #Frequency (3.6.6.1)
    channel_table = Instrument.control(
        "SOUR:FREQ:CHAN:TABL ?",
        "SOUR:FREQ:CHAN:TABL %s",
        """A string property controlling which channel table is used

        Possible selections are:

        ======  =======
        Value   Meaning
        ======  =======
        DEF     Default channel table
        USR1    User table No. 1
        USR2    User table No. 2
        USR3    User table No. 3
        USR4    User table No. 4
        USR5    User table No. 5
        ======  =======
        """,
        validator = strict_discrete_set,
        values = ["DEF","USR1","USR2","USR3","USR4","USR5"],
        )

    normal_channel = Instrument.control(
        "SOUR:FREQ:CHAN:NORM ?",
        "SOUR:FREQ:CHAN:NORM %d",
        """A int property controlling the current selected regular/normal channel number
        valid selections are based on the country settings.
        """,
        )

    special_channel = Instrument.control(
        "SOUR:FREQ:CHAN:NORM ?",
        "SOUR:FREQ:CHAN:NORM %d",
        """A int property controlling the current selected special channel number
        valid selections are based on the country settings.
        """,
        )

    def channel_up_relative(self):
        """
        Increases the outpout frequency to the next higher channel/special channel
        based on the current country settings
        """
        Instrument.write(self,"SOUR:CHAN:REL UP")

    def channel_down_relative(self):
        """
        Decreases the outpout frequency to the next low channel/special channel
        based on the current country settings
        """
        Instrument.write(self,"SOUR:CHAN:REL DOWN")

    channel_sweep_start = Instrument.control(
        "SOUR:FREQ:CHAN:STAR?",
        "SOUR:FREQ:CHAN:STAR %g",
        """A float property controlling the start frequency for channel sweep in Hz

        * Minimum 5 MHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [5E6, 1E9]
        )

    channel_sweep_stop =  Instrument.control(
        "SOUR:FREQ:CHAN:STOP?",
        "SOUR:FREQ:CHAN:STOP %g",
        """A float property controlling the start frequency for channel sweep in Hz

        * Minimum 5 MHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [5E6, 1E9]
        )

    channel_sweep_step = Instrument.control(
        "SOUR:FREQ:CHAN:STEP?",
        "SOUR:FREQ:CHAN:STEP %g",
        """A float property controlling the start frequency for  channel sweep in Hz

        * Minimum 5 MHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [5E6, 1E9]
        )

    cw_frequency = Instrument.control(
        "SOUR:FREQ:CW?",
        "SOUR:FREQ:CW %g",
        """A float property controlling the CW-frequency in Hz

        * Minimum 5 MHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [5E6, 1E9]
        )

    frequency = Instrument.control(
        "SOUR:FREQ:FIXED?",
        "SOUR:FREQ:FIXED %g",
        """A float property controlling the frequency in Hz

        * Minimum 5 MHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [5E6, 1E9]
        )

    frequency_mode = Instrument.control(
        "SOUR:FREQ:MODE?",
        "SOUR:FREQ:MODE %s",
        """A string property controlling which the unit is used in

        Possible selections are:

        ======  =======
        Value   Meaning
        ======  =======
        CW      Continous wave mode
        FIXED   fixed frequency mode
        CHSW    Channel sweep
        RFSW    Frequency sweep
        ======  =======

        _Note_: selecting the sweep mode, will start the sweep imemdiately!
        """,
        validator = strict_discrete_set,
        values = ["CW","FIXED","CHSW","RFSW"],
        )

    high_f_res = Instrument.control(
        "SOUR:FREQ:RES?",
        "SOUR:FREQ:RES %s",
        """ A property that controls the modulation status,

        Possible selections are:

        ======  =======
        Value   Meaning
        ======  =======
        False   Low resolution (1000Hz)
        True    High resoultion (1Hz)
        ======  =======
        """,
        validator = strict_discrete_set,
        values={False:"LOW", True:"HIGH"},
        map_values = True,
        )

    rf_sweep_center = Instrument.control(
        "SOUR:FREQ:CENTER?",
        "SOUR:FREQ:CENTER %g",
        """A float property controlling the center frequency for sweep in Hz

        * Minimum 5 MHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [5E6, 1E9]
        )

    rf_sweep_start = Instrument.control(
        "SOUR:FREQ:STAR?",
        "SOUR:FREQ:STAR %g",
        """A float property controlling the start frequency for sweep in Hz

        * Minimum 5 MHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [5E6, 1E9]
        )

    rf_sweep_stop = Instrument.control(
        "SOUR:FREQ:STOP?",
        "SOUR:FREQ:STOP %g",
        """A float property controlling the stop frequency for sweep in Hz

        * Minimum 5 MHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [5E6, 1E9]
        )

    rf_sweep_step = Instrument.control(
        "SOUR:FREQ:STEP?",
        "SOUR:FREQ:STEP %g",
        """A float property controlling the stepwidth for sweep in Hz,

        * Minimum 1 kHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [1E3, 1E9]
        )

    span = Instrument.control(
        "SOUR:FREQ:SPAN?",
        "SOUR:FREQ:SPAN %g",
        """A float property controlling the sweep span in Hz,

        * Minimum 1 kHz
        * Maximum 1 GHz
        """,
        validator = strict_range,
        values = [1E3, 1E9]
        )

    #Level (3.6.6.2)
    level = Instrument.control(
        "SOUR:POW:LEV?",
        "SOUR:POW:LEV %g DBM",
        """A float property controlling the output level in dBm,

        * Minimum -99dBm
        * Maximum 10dBm (depending on output mode)
        """,
        validator = strict_range,
        values = [-99, 10],
        )

    level_mode = Instrument.control(
        "SOUR:POW:LEV:MODE?",
        "SOUR:POW:LEV:MODE %s",
        """A string property controlling the output attenuator and linearity mode

        Possible selections are:

        ======  ====================  =================
        Value   Meaning               max. output level
        ======  ====================  =================
        NORM    Normal mode           +6 dBm
        LOWN    low noise mode        +10 dBm
        CONT    continous mode        +10 dBm
        LOWD    low distortion mode   +0 dBm
        ======  ====================  =================

        Contiuous mode allows up to 14 dB of level setting without use of the mechanical attenuator.

        """,
        validator = strict_discrete_set,
        values = ["NORM","LOWN","CONT","LOWD"]
        )

    rf_out = Instrument.control(
        "SOUR:POW:STAT?",
        "SOUR:POW:STATE %s",
        """ A bool property that controls the status of the RF-output,

        ======  =======
        Value   Meaning
        ======  =======
        False   RF-output disabled
        True    RF-output enabled
        ======  =======
        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    #for later add SOUR:TEL:IMOD (3.6.6.3 Intermodulation subsystem)

    #Coder (3.6.6.4)
    def coder_adjust(self):
        """
        Starts the automatic setting of the differential deviation
        """
        self.write("SOUR:TEL:MOD:COD:ADJ")

    coder_id_frequency = Instrument.control(
        "SOUR:TEL:MOD:COD:IDENT:FREQ?",
        "SOUR:TEL:MOD:COD:IDENT:FREQ %d",
        """ A int property that controls the frequency of the identification of the coder

        valid range 0 .. 200 Hz
        """,
        validator = strict_range,
        values=[0, 200],
        )

    coder_modulation_degree = Instrument.control(
        "SOUR:TEL:MOD:COD:MOD:DEGR?",
        "SOUR:TEL:MOD:COD:MOD:DEGR %g",
        """ A float property that controls the modulation degree of the identification of the coder

        valid range: 0 .. 0.9
        """,
        validator = strict_range,
        values=[0, 0.9],
        )

    coder_pilot_frequency = Instrument.control(
        "SOUR:TEL:MOD:COD:PIL:FREQ?",
        "SOUR:TEL:MOD:COD:PIL:FREQ %d",
        """ A int property that controls the pilot frequency of the coder

        valid range: 40 .. 60 kHz
        """,
        validator = strict_range,
        values=[5E4, 6E4],
        )

    coder_pilot_deviation = Instrument.control(
        "SOUR:TEL:MOD:COD:PIL:FREQ:DEV?",
        "SOUR:TEL:MOD:COD:PIL:FREQ:DEV %d",
        """ A int property that controls deviation of the pilot frequency of the coder

        valid range: 1 .. 4 kHz
        """,
        validator = strict_range,
        values=[1E3, 4E3],
        )

    #External modulation (3.6.6.5)
    external_modulation_power = Instrument.control(
        "SOUR:TEL:MOD:EXT:POW?",
        "SOUR:TEL:MOD:EXT:POW %d",
        """ A int property that controls the setting for the external modulator output power

        valid range: -7..0 dBm
        """,
        validator = strict_range,
        values=[-7, 0],
        )

    external_modulation_frequency = Instrument.control(
        "SOUR:TEL:MOD:EXT:FREQ?",
        "SOUR:TEL:MOD:EXT:FREQ %d",
        """ A int property that controls the setting for the external modulator output power

        valid range: 32 .. 46 MHz
        """,
        validator = strict_range,
        values=[32e6, 46e6],
        )

    #NICAM system (3.6.6.6)
    nicam_mode = Instrument.control(
        "SOUR:TEL:MOD:NIC:AUD:MODE?",
        "SOUR:TEL:MOD:NIC:AUD:MODE %s",
        """ A string property that controls the signal type to be sent via NICAM

        Possible values are:

        ======  =======
        Value   Meaning
        ======  =======
        MON     Mono sound + NICAM data
        STER    Stereo sound
        DUAL    Dual channel sound
        DATA    NICAM data only
        ======  =======

        """,
        validator = strict_discrete_set,
        values=["MON","STER","DUAL","DATA"],
        )

    nicam_audio_frequency = Instrument.control(
        "SOUR:TEL:MOD:NIC:AUD:FREQ?",
        "SOUR:TEL:MOD:NIC:AUD:FREQ %d",
        """ A int property that controls the frequency of the internal sound generator

        valid range: 0 Hz .. 15 kHz
        """,
        validator = strict_range,
        values=[0, 1.5E4],
        )

    nicam_preemphasis_enabled = Instrument.control(
        "SOUR:TEL:MOD:NIC:AUD:PRE?",
        "SOUR:TEL:MOD:NIC:AUD:PRE %d",
        """ A bool property that controls the status of the J17 preemphasis,

        ======  =======
        Value   Meaning
        ======  =======
        False   preemphasis disabled
        True    preemphasis enabled
        ======  =======
        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    nicam_audio_volume = Instrument.control(
        "SOUR:TEL:MOD:NIC:AUD:VOL?",
        "SOUR:TEL:MOD:NIC:AUD:VOL %g",
        """ A float property that controls the audio volume in the NICAM  modulator

        valid range: 0..60 dB
        """,
        validator = strict_range,
        values=[0, 60],
        )

    nicam_data = Instrument.control(
        "SOUR:TEL:MOD:NIC:AUD:DATA?",
        "SOUR:TEL:MOD:NIC:AUD:DATA %d",
        """ A int property that controls the data in the NICAM  modulator

        valid range: 0 .. 2047
        """,
        validator = strict_range,
        values=[0, 2047],
        cast=int
        )


    nicam_additional_bits = Instrument.control(
        "SOUR:TEL:MOD:NIC:AUD:ADD?",
        "SOUR:TEL:MOD:NIC:AUD:ADD %d",
        """ A int property that controls the additional data in the NICAM  modulator

        valid range: 0 .. 2047
        """,
        validator = strict_range,
        values=[0, 2047],
        )

    nicam_control_bits = Instrument.control(
        "SOUR:TEL:MOD:NIC:AUD:CONT?",
        "SOUR:TEL:MOD:NIC:AUD:CONT %d",
        """ A int property that controls the additional data in the NICAM  modulator

        valid range: 0 .. 3
        """,
        validator = strict_range,
        values=[0, 3],
        )

    nicam_bit_error_rate = Instrument.control(
        "SOUR:TEL:MOD:NIC:BIT?",
        "SOUR:TEL:MOD:NIC:BIT %g",
        """ A float property that controls the additional data in the NICAM  modulator

        valid range: 1.2E-7 .. 2E-3
        """,
        validator = strict_range,
        values=[1.2E-7, 2E-3],
        )

    nicam_bit_error_enabled = Instrument.control(
        "SOUR:TEL:MOD:NIC:BIT:STAT?",
        "SOUR:TEL:MOD:NIC:BIT:STAT %d",
        """ A bool property that controls the status of an artifical bit error rate to be applied,

        ======  =======
        Value   Meaning
        ======  =======
        False   artificial BER disabled
        True    artificial BER enabled
        ======  =======
        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )


    nicam_carrier_frequency = Instrument.control(
        "SOUR:TEL:MOD:NIC:CARR:FREQ?",
        "SOUR:TEL:MOD:NIC:CARR:FREQ %g",
        """ A float property that controls the frequency of the NICAM carrier

        valid range: 33.05 MHz +/- 0.2 Mhz
        """,
        validator = strict_range,
        values=[32.85E6, 33.25E6],
        )

    nicam_intercarrier_frequency = Instrument.control(
        "SOUR:TEL:MOD:NIC:INT:FREQ?",
        "SOUR:TEL:MOD:NIC:INT:FREQ %g",
        """ A float property that controls the inter-carrier frequency of the NICAM carrier

        valid range: 5 .. 9 MHz
        """,
        validator = strict_range,
        values=[5E6, 9E6],
        )

    nicam_carrier_level = Instrument.control(
        "SOUR:TEL:MOD:NIC:CARR:LEV?",
        "SOUR:TEL:MOD:NIC:CARR:LEV %g",
        """ A float property that controls the value of the NICAM carrier

        valid range: -40 .. -13 dB
        """,
        validator = strict_range,
        values=[-40, 13],
        )

    nicam_carrier_enabled = Instrument.control(
        "SOUR:TEL:MOD:NIC:CARR:STAT?",
        "SOUR:TEL:MOD:NIC:CARR:STAT %s",
        """ A bool property that controls if the NICAM carrier is switched on or off

        ======  =======
        Value   Meaning
        ======  =======
        False   NICAM carrier disabled
        True    NICAM carrier enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    nicam_IQ_inverted = Instrument.control(
        "SOUR:TEL:MOD:NIC:MODE?",
        "SOUR:TEL:MOD:NIC:MODE %s",
        """ A bool property that controls if the NICAM IQ signals are inverted or not

        ======  =======
        Value   Meaning
        ======  =======
        False   normal (IQ)
        True    inverted (QI)
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:"IQ", True:"QI"},
        map_values = True,
        )

    nicam_source = Instrument.control(
        "SOUR:TEL:MOD:NIC:SOUR?",
        "SOUR:TEL:MOD:NIC:SOUR %s",
        """ A string property that controls the signal source for NICAM

        Possible values are:

        ======  =======
        Value   Meaning
        ======  =======
        INT     Internal audio generator(s)
        EXT     External audio source
        CW      Continous wave signal
        RAND    Random data stream
        TEST    Test signal
        ======  =======

        """,
        validator = strict_discrete_set,
        values=["INT","EXT","CW","RAND","TEST"],
        )

    nicam_test_signal = Instrument.control(
        "SOUR:TEL:MOD:NIC:TEST?",
        "SOUR:TEL:MOD:NIC:TEST %s",
        """ A int property that controls the selection of the test sinal applied

        ======  =======
        Value   Meaning
        ======  =======
        1       Test signal 1 (91 kHz square wave, I&Q 90deg apart)
        2       Test signal 2 (45.5 kHz square wave, I&Q 90deg apart)
        3       Test signal 3 (182 kHz sine wave, I&Q in phase)
        ======  =======

        """,
        validator = strict_discrete_set,
        values={1:"TST1", 2:"TST2", 3:"TST3"},
        map_values = True,
        )

    #Sound (3.6.6.7)
    sound_modulation_degree = Instrument.control(
        "SOUR:TEL:MOD:SOUN:AUD:DEGR?",
        "SOUR:TEL:MOD:SOUN:AUD:DEGR %g",
        """ A float property that controls the modulation depth for the audi signal
        (Note: only for the use of AM in Standard L)

        valid range: 0 .. 1 (100%)
        """,
        validator = strict_range,
        values=[0, 1],
        )

    audio_deviation = Instrument.control(
        "SOUR:TEL:MOD:SOUN:AUD:DEV?",
        "SOUR:TEL:MOD:SOUN:AUD:DEV %d",
        """ A int property that controls deviation of the selected audio signal

        valid range: 0 .. 110 kHz
        """,
        validator = strict_range,
        values=[0, 1.1E5],
        )

    audio_frequency = Instrument.control(
        "SOUR:TEL:MOD:SOUN:AUD:FREQ?",
        "SOUR:TEL:MOD:SOUN:AUD:FREQ %d",
        """ A int property that controls the frequency of the internal sound generator

        valid range: 300 Hz .. 15 kHz
        """,
        validator = strict_range,
        values=[300, 1.5E4],
        )

    audio_source = Instrument.control(
        "SOUR:TEL:MOD:SOUN:AUD:FREQ:SOUR?",
        "SOUR:TEL:MOD:SOUN:AUD:FREQ:SOUR %s",
        """ A bool property for the audio source selection,

        ======  =======
        Value   Meaning
        ======  =======
        False   Internal audio generator(s)
        True    External signal source
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:"INT", True:"EXT"},
        map_values = True,
        )

    audio_modulation = Instrument.control(
        "SOUR:TEL:MOD:SOUN:AUD:FREQ:STAT?",
        "SOUR:TEL:MOD:SOUN:AUD:FREQ:STAT %s",
        """ A bool property that controls the audio modulation status

        ======  =======
        Value   Meaning
        ======  =======
        False   modulation disabled
        True    modulation enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    audio_carrier_frequency = Instrument.control(
        "SOUR:TEL:MOD:SOUN:CARR:FREQ?",
        "SOUR:TEL:MOD:SOUN:CARR:FREQ %g",
        """ A float property that controls the frequency of the sound carrier

        valid range: 32 .. 46 MHz
        """,
        validator = strict_range,
        values=[38.75E6, 52.75E6],
        )

    audio_carrier_level = Instrument.control(
        "SOUR:TEL:MOD:SOUN:CARR:LEV?",
        "SOUR:TEL:MOD:SOUN:CARR:LEV %g",
        """ A float property that controls the value of the audio carrier

        valid range: -34 .. -6 dB
        """,
        validator = strict_range,
        values=[-34, 6],
        )

    audio_carrier_enabled = Instrument.control(
        "SOUR:TEL:MOD:SOUN:CARR:STAT?",
        "SOUR:TEL:MOD:SOUN:CARR:STAT %s",
        """ A bool property that controls if the audio carrier is switched on or off

        ======  =======
        Value   Meaning
        ======  =======
        False   audio carrier disabled
        True    audio carrier enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    audio_preemphasis_time = Instrument.control(
        "SOUR:TEL:MOD:SOUN:PRE:MODE?",
        "SOUR:TEL:MOD:SOUN:PRE:MODE %s",
        """ A bool property that controls if the mode of the preemphasis for the audio signal

        ======  =======
        Value   Meaning
        ======  =======
        50      50 us preemphasis
        75      75 us preemphasis
        ======  =======

        """,
        validator = strict_discrete_set,
        values={50:"US50",75:"US75"},
        map_values = True,
        )

    audio_preemphasis_enabled = Instrument.control(
        "SOUR:TEL:MOD:SOUN:PRE:STAT?",
        "SOUR:TEL:MOD:SOUN:PRE:STAT %s",
        """ A bool property that controls if the preemphasis for the audui is switched on or off

        ======  =======
        Value   Meaning
        ======  =======
        False   audio carrier disabled
        True    audio carrier enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    #Modulation (3.6.6.8)
    modulation_source = Instrument.control(
        "SOUR:MOD:SOUR?",
        "SOUR:MOD:SOUR %s",
        """ A bool property for the modulation source selection,

        ======  =======
        Value   Meaning
        ======  =======
        False   Internal modulator
        True    External modulator
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:"INT", True:"EXT"},
        map_values = True,
        )

    modulation = Instrument.control(
        "SOUR:MOD:STAT?",
        "SOUR:MOD:STAT %s",
        """ A bool property that controls the modulation status

        ======  =======
        Value   Meaning
        ======  =======
        False   modulation disabled
        True    modulation enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    #VISION subsystem (3.6.6.9)
    vision_carrier = Instrument.control(
        "SOUR:TEL:MOD:VIS:CARR:STAT?",
        "SOUR:TEL:MOD:VIS:CARR:STAT %s",
        """ A bool property that controls the vision carrier status

        ======  =======
        Value   Meaning
        ======  =======
        False   Vision carrier disabled
        True    Vision carrier enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    vision_carrier_frequency = Instrument.control(
        "SOUR:TEL:MOD:VIS:CARR:FREQ?",
        "SOUR:TEL:MOD:VIS:CARR:FREQ %g",
        """ A float property that controls the frequency of the vision carrier

        valid range: 32 .. 46 MHz
        """,
        validator = strict_range,
        values=[32E6, 46E6],
        )

    vision_average = Instrument.control(
        "SOUR:TEL:MOD:VIS:AVER:STAT?",
        "SOUR:TEL:MOD:VIS:AVER:STAT %s",
        """ A bool property that controls the average mode for the vision system

        ======  =======
        Value   Meaning
        ======  =======
        False   Average function disabled
        True    Average function enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    vision_balance = Instrument.control(
        "SOUR:TEL:MOD:VIS:BAL?",
        "SOUR:TEL:MOD:VIS:BAL %g",
        """ A float property that controls the balance of the vision modulator

        valid range: -0.5 .. 0.5
        """,
        validator = strict_range,
        values=[-0.5, 0.5],
        )

    vision_clamping_average = Instrument.control(
        "SOUR:TEL:MOD:VIS:CLAM:AVER?",
        "SOUR:TEL:MOD:VIS:CLAM:AVER %g",
        """ A float property that controls the operation point of the vision modulator

        valid range: -0.5 .. 0.5
        """,
        validator = strict_range,
        values=[-0.5, 0.5],
        )

    vision_clamping_enabled = Instrument.control(
        "SOUR:TEL:MOD:VIS:CLAM:STAT?",
        "SOUR:TEL:MOD:VIS:CLAM:STAT %s",
        """ A bool property that controls the clamping behavior of the vision modulator,

        ======  =======
        Value   Meaning
        ======  =======
        False   Clamping disabled
        True    Clamping enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    vision_clamping_mode = Instrument.control(
        "SOUR:TEL:MOD:VIS:CLAM:TYPE?",
        "SOUR:TEL:MOD:VIS:CLAM:TYPE %s",
        """ A string property that controls the clamping mode of the vision modulator

        Possible selections are HARD or SOFT

        """,
        validator = strict_discrete_set,
        values=["HARD","SOFT"],
        )


    vision_precorrection_enabled = Instrument.control(
        "SOUR:TEL:MOD:VIS:PREC?",
        "SOUR:TEL:MOD:VIS:PREC %s",
        """ A bool property that controls the precorrection behavior of the vision modulator

        ======  =======
        Value   Meaning
        ======  =======
        False   Precorrection disabled
        True    Precorrection enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    vision_residual_carrier_level = Instrument.control(
        "SOUR:TEL:MOD:VIS:RES?",
        "SOUR:TEL:MOD:VIS:RES %g",
        """ A float property that controls the value of the residual carrier

        valid range: 0 .. 0.3 (30%)
        """,
        validator = strict_range,
        values=[-0, 0.3],
        )

    vision_videosignal_enabled = Instrument.control(
        "SOUR:TEL:MOD:VIS:VID?",
        "SOUR:TEL:MOD:VIS:VID %s",
        """ A bool property that controls if the video signal is switched on or off

        ======  =======
        Value   Meaning
        ======  =======
        False   video signal disabled
        True    video signal enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    vision_sideband_filter_enabled = Instrument.control(
        "SOUR:TEL:MOD:VIS:VSBF?",
        "SOUR:TEL:MOD:VIS:VSBF %s",
        """ A bool property that controls the use of the VSBF (vestigal sideband filter)
        in the vision modulator

        ======  =======
        Value   Meaning
        ======  =======
        False   VSBF disabled
        True    VSBF enabled
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    #Television subsystem (3.6.6.10)
    lower_sideband = Instrument.control(
        "SOUR:TEL:SID?",
        "SOUR:TEL:SID %s",
        """ A bool property that controls the use of the lower sideband

        ======  =======
        Value   Meaning
        ======  =======
        False   upper side band (USB)
        True    lower side band (LSB)
        ======  =======

        """,
        validator = strict_discrete_set,
        values={False:"UPP", True:"LOW"},
        map_values = True,
        )

    sound_mode = Instrument.control(
        "SOUR:TEL:SOUN?",
        "SOUR:TEL:SOUN %s",
        """ A string property that controls the type of audio signal

        Possible values are:

        ======  =======
        Value   Meaning
        ======  =======
        MONO    MOnoaural sound
        PIL     pilot-carrier + mono
        BTSC    BTSC + mono
        STER    Stereo sound
        DUAL    Dual channel sound
        NIC     NICAM + Mono
        ======  =======

        """,
        validator = strict_discrete_set,
        values=["MONO","PIL","BTSC","STER","DUAL","NIC"],
        )

    TV_standard = Instrument.control(
        "SOUR:TEL:STAN?",
        "SOUR:TEL:STAN %s",
        """ A string property that controls the type of video standard

        Possible values are:
        BG, DK, I, K1, L, M, N
        """,
        validator = strict_discrete_set,
        values=["BG","DK","I","K1","L","M","N"],
        )

    TV_country = Instrument.control(
        "SOUR:TEL:STAN:COUN?",
        "SOUR:TEL:STAN:COUN %s",
        """ A string property that controls the country specifics of the
        video/sound system to be used

        Possible values are:

        ======  =======
        Value   Meaning
        ======  =======
        BG_G    BG General
        DK_G    DK General
        I_G     I General
        L_G     L General
        GERM    Germany
        BELG    Belgium
        NETH    Netherlands
        FIN     Finland
        AUST    Australia
        BG_T    BG Th
        DENM    Denmark
        NORW    Norway
        SWED    Sweden
        GUS     Russia
        POL1    Poland
        POL2    Poland
        HUNG    Hungary
        CHEC    Czech Republic
        CHINA1  China
        CHINA2  China
        GRE     Great Britain
        SAFR    South Africa
        FRAN    France
        USA     United States
        KOR     Korea
        JAP     Japan
        CAN     Canada
        SAM     South America
        ======  =======

        Please confim with the manual about the details for these settings.
        """,
        validator = strict_discrete_set,
        values=["BG_G", "DK_G", "I_G", "L_G", "GERM","BELG", "NETH",
        "FIN", "AUST", "BG_T", "DENM", "NORW", "SWED", "GUS", "POL1", "POL2",
        "HUNG", "CHEC", "CHINA1", "CHINA2" , "GRE", "SAFR", "FRAN", "USA",
        "KOR" , "JAP", "CAN", "SAM"],
            )

    #output voltage (3.6.6.12)
    output_voltage = Instrument.control(
        "SOUR:VOLT:LEV?",
        "SOUR:VOLT:LEV %g",
        """A float property controlling the output level in Volt,

        Minimum 2.50891e-6, Maximum 0.707068 (depending on output mode)
        """,
        validator = strict_range,
        values = [2.508910e-6,0.7070168],
        )

    #STATUS entries (3.6.7)
    event_reg = Instrument.measurement(
        "STAT:OPER:EVEN?",
        """
        Content of the event register of the Status Operation Register
        """,
        cast=int,
        )

    status_reg = Instrument.measurement(
        "STAT:OPER:COND?",
        """
        Content of the condition register of the Status Operation Register
        """,
        cast=int,
        )

    operation_enable_reg = Instrument.control(
        "STAT:OPER:ENAB?",
        "STAT:OPER:ENAB %d",
        """
        Content of the enable register of the Status Operation Register
        valid range: 0...32767
        """,
        cast=int,
        validator = strict_range,
        values=[0, 32767]
        )

    def status_preset(self):
        """ partly resets the SCPI status reporting structures

        """
        self.write("STAT:PRES")

    questionable_event_reg = Instrument.measurement(
        "STAT:QUES:EVEN?",
        """
        Content of the event register of the Status Questionable Operation Register
        """,
        cast=int,
        )

    questionanble_status_reg = Instrument.measurement(
        "STAT:QUES:COND?",
        """
        Content of the condition register of the Status Questionable Operation Register
        """,
        cast=int,
        )

    questionable_operation_enable_reg = Instrument.control(
        "STAT:QUES:ENAB?",
        "STAT:QUES:ENAB %d",
        """
        Content of the enable register of the Status Questionable Operation Register
        valid range 0...32767
        """,
        cast=int,
        validator = strict_range,
        values=[0, 32767]
        )


    #SYSTEM entries (3.6.8)
    beeper = Instrument.control(
        "SYST:BEEP:STATE?",
        "SYST:BEEP:STATE %s",
        """ A bool property that controls the beeper status,

        ======  =======
        Value   Meaning
        ======  =======
        False   beeper disabled
        True    beeper enabled
        ======  =======
        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    display_update = Instrument.control(
        "SYST:DISP:UPDATE:STATE?",
        "SYST:DISP:UPDATE:STATE %s",
        """ A bool property that controls the status of the displayed values

        ======  =======
        Value   Meaning
        ======  =======
        False   no infomation shown on the display during remote
        True    status info shown on display
        ======  =======
        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    gpib_address = Instrument.control(
        "SYST:COMM:GPIB:ADDR?",
        "SYST:COMM:GPIB:ADDR %d",
        """ A int property that controls the GPIB address of the unit

        valid range:  0..30
        """,
        validator = strict_range,
        values=[0, 30],
        )

    remote_interfaces = Instrument.control(
        "SYST:COM:REM?",
        "SYST:COM:REM %s",
        """A string property controlling the selection of interfaces for remote control

        Possible selections are:

        ======  =======
        Value   Meaning
        ======  =======
        OFF     no remote control
        GPIB    GPIB only enabled
        SER     RS232 only anbled
        BOTH    GPIB & RS232 enabled
        ======  =======
        """,
        validator = strict_discrete_set,
        values = ["OFF","GPIB","SER","BOTH"]
        )

    serial_baud = Instrument.control(
        "SYST:COMM:SER:BAUD?",
        "SYST:COMM:SER:BAUD %g",
        """ A int property that controls the serial communication speed ,

        Possible values are: 110,300,600,1200,4800,9600,19200
        """,
        validator = strict_discrete_set,
        values=[110,300,600,1200,4800,9600,19200],
        )

    serial_bits = Instrument.control(
        "SYST:COMM:SER:BITS?",
        "SYST:COMM:SER:BITS %g",
        """ A int property that controls the number of bits used in serial communication

        Possible values are: 7 or 8
        """,
        validator = strict_discrete_set,
        values=[7,8],
        )

    serial_flowcontrol = Instrument.control(
        "SYST:COMM:SER:PACE?",
        "SYST:COMM:SER:PACE %s",
        """ A string property that controls the serial handshake type used in serial communication

        Possible values are:

        ======  =======
        Value   Meaning
        ======  =======
        NONE    no flow-control/handshake
        XON     XON/XOFF flow-control
        ACK     hardware handshake with RTS&CTS
        ======  =======

        """,
        validator = strict_discrete_set,
        values=["NONE","XON","ACK"],
        )

    serial_parity = Instrument.control(
        "SYST:COMM:SER:PAR?",
        "SYST:COMM:SER:PAR %s",
        """ A string property that controls the parity type used for serial communication

        Possible values are:

        ======  =======
        Value   Meaning
        ======  =======
        NONE    no parity
        EVEN    even parity
        ODD     odd parity
        ONE     parity bit fixed to 1
        ZERO    parity bit fixed to 0
        ======  =======

        """,
        validator = strict_discrete_set,
        values=["NONE","EVEN","ODD","ONE","ZERO"],
        )

    serial_stopbits = Instrument.control(
        "SYST:COMM:SER:SBIT?",
        "SYST:COMM:SER:SBIT %g",
        """ A int property that controls the number of stop-bits used in serial communication,

        Possible values are: 1 or 2
        """,
        validator = strict_discrete_set,
        values=[1,2],
        )

    date = Instrument.measurement(
        "SYST:DATE?",
        """
        A tuple property for the date of the RTC in the unit

        """,
        )


    time = Instrument.measurement(
        "SYST:TIME?",
        """
        A tuple property for the time of the RTC in the unit

        """,
        )


    #Unit subsystem (3.6.9)
    scale_volt = Instrument.control(
        "UNIT:VOLT?",
        "UNIT:VOLT %s",
        """ A string property that controls the unit to be used for voltage entries on the unit

        Possible values are:
        AV,FV, PV, NV, UV, MV, V, KV, MAV, GV, TV, PEV, EV,
        DBAV, DBFV, DBPV, DBNV, DBUV, DBMV, DBV, DBKV, DBMAv, DBGV, DBTV, DBPEv, DBEV
        """,
        validator = strict_discrete_set,
        values= ["AV","FV", "PV", "NV", "UV", "MV", "V", "KV", "MAV", "GV",
                 "TV", "PEV", "EV", "DBAV", "DBFV", "DBPV", "DBNV", "DBUV",
                 "DBMV", "DBV", "DBKV", "DBMAv", "DBGV", "DBTV", "DBPEv", "DBEV"],
        )

    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                log.error("R&S SFM: %s: %s \n" % (err[0],err[1]) )
            else:
                break
