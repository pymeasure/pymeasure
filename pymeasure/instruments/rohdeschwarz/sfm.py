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

    .. code-block:: python

    """

    def __init__(self, resourceName, **kwargs):
        super(SFM, self).__init__(
            resourceName,
            "Rohde&Schwarz SFM",
            includeSCPI = True,
            **kwargs
        )
            # send_end = True,
            # read_termination = "\r\n",

    def calibration(self,number=1,subsystem=None):
        """
        Function to either calibrate the whole modulator, when subsystem paramtrer is omitted,
        or calibrate a subsystem of the modulator.
        Valid subssyem selectiosn include: "NICam, VISion, SOUNd1|2, CODer"

        """
        if subsystem is None:
            self.write("CAL:MOD%d" % (number))
        else:
            self.write("CAL:MOD%d:%s" % (number,strict_discrete_set(subsystem,["NIC","VIS","SOUN1","SOUN2","COD"])))

    #INST (Manual 3.6.4)
    system_number = Instrument.control(
        "INST:SEL ?",
        "INST:SEL: SYS%d",
        """A int property for the selected systems (if more then 1 available),
        Minimum 1, Maximum 6""",
        validator = strict_range,
        values = [1, 6],
        check_set_errors=True,
        )

    #ROUTE (Manual 3.6.5)
    R75_out = Instrument.control(
        "ROUT:CHAN:OUTP:IMP?",
        "ROUT:CHAN:OUTP:IMP %s",
        """ A bool property that controls the use of the 75R output (if installed),
        False => 50R output active (N),
        True => 75R output active (BNC)
        """,
        validator = strict_discrete_set,
        values={False:"LOW", True:"HIGH"},
        map_values = True,
        )

    ext_ref_basic = Instrument.control(
        "ROUT:REF:CLOCK:BAS?",
        "ROUT:REF:CLOCK:BAS %s",
        """ A bool property for the external reference for the basic unit,
        False => Internal 10 MHz is used,
        True => External 10 MHz is used
        """,
        validator = strict_discrete_set,
        values={False:"INT", True:"EXT"},
        map_values = True,
        )

    ext_ref_extenstion = Instrument.control(
        "ROUT:REF:CLOCK:EXT?",
        "ROUT:REF:CLOCK:EXT %s",
        """ A bool property for the external reference for the extension frame,
        False => Internal 10 MHz is used,
        True => External 10 MHz is used
        """,
        validator = strict_discrete_set,
        values={False:"INT", True:"EXT"},
        map_values = True,
        )

    ext_vid_connector = Instrument.control(
        "ROUT:TEL:VID:EXT?",
        "ROUT:TEL:VID:EXT %s",
        """A string property controlling which connector is used as the input of the video source,
        Possible selections are HIGH, LOW, REAR1, REAR2, AUTO (based on the setting in stndard)""",
        validator = strict_discrete_set,
        values = ["HIGH","LOW","REAR1","REAR2","AUTO"],
        )

    #SOURCE:FREQ (3.6.6.1)
    channel_table = Instrument.control(
        "SOUR:FREQ:CHAN:TABL ?",
        "SOUR:FREQ:CHAN:TABL %s",
        """A string property controlling which channel table is used,
        Possible selections are DEFault, USR1..USR5""",
        validator = strict_discrete_set,
        values = ["DEF","USR1","USR2","USR3","USR4","USR5"],
        )

    #TODO add more channel properties

    cw_frequency = Instrument.control(
        "SOUR:FREQ:CW?",
        "SOUR:FREQ:CW %g",
        """A float property controlling the CW-frequency in Hz,
        Minimum 5 MHz, Maximum 1 GHz""",
        validator = strict_range,
        values = [5E6, 1E9]
        )

    #TODO enhance for more then 1 system
    frequency = Instrument.control(
        "SOUR:FREQ:FIXED?",
        "SOUR:FREQ:FIXED %g",
        """A float property controlling the frequency in Hz,
        Minimum 5 MHz, Maximum 1 GHz""",
        validator = strict_range,
        values = [5E6, 1E9]
        )

    freq_mode = Instrument.control(
        "SOUR:FREQ:MODE ?",
        "SOUR:FREQ:MODE %s",
        """A string property controlling which the unit is used in,
        Possible selections are CW, FIXED, CHSW (channel sweep), RFSW (frequency sweep)
        Note: selecting the sweep mode, will start the sweep imemdiately""",
        validator = strict_discrete_set,
        values = ["CW","FIXED","CHSW","RFSW"],
        )

    high_f_res = Instrument.control(
        "SOUR:FREQ:RES?",
        "SOUR:FREQ:RES %s",
        """ A property that controls the modulation status,
        False => low resolution (1000Hz),
        True => High resoultion (1Hz)
        """,
        validator = strict_discrete_set,
        values={False:"LOW", True:"HIGH"},
        map_values = True,
        )

    center_f = Instrument.control(
        "SOUR:FREQ:CENTER?",
        "SOUR:FREQ:CENTER %g",
        """A float property controlling the center frequency (for sweep) in Hz,
        Minimum 5 MHz, Maximum 1 GHz""",
        validator = strict_range,
        values = [5E6, 1E9]
        )

    start_f = Instrument.control(
        "SOUR:FREQ:STAR?",
        "SOUR:FREQ:STAR %g",
        """A float property controlling the start frequency (for sweep) in Hz,
        Minimum 5 MHz, Maximum 1 GHz""",
        validator = strict_range,
        values = [5E6, 1E9]
        )

    stop_f = Instrument.control(
        "SOUR:FREQ:STOP?",
        "SOUR:FREQ:STOP %g",
        """A float property controlling the stop frequency (for sweep)in Hz,
        Minimum 5 MHz, Maximum 1 GHz""",
        validator = strict_range,
        values = [5E6, 1E9]
        )

    step_f = Instrument.control(
        "SOUR:FREQ:STEP?",
        "SOUR:FREQ:STEP %g",
        """A float property controlling the stepwidth (for sweep) in Hz,
        Minimum 5 MHz, Maximum 1 GHz""",
        validator = strict_range,
        values = [1E3, 1E9]
        )

    span = Instrument.control(
        "SOUR:FREQ:SPAN?",
        "SOUR:FREQ:SPAN %g",
        """A float property controlling the frequency in Hz,
        Minimum 5 MHz, Maximum 1 GHz""",
        validator = strict_range,
        values = [1E3, 1E9]
        )

    #SOUR:POW (3.6.6.2)
    level = Instrument.control(
        "SOUR:POW:LEV?",
        "SOUR:POW:LEV %g DBM",
        """A float property controlling the output level in dBm,
        Minimum -99dBm, Maximum 10dBm (depending on output mode)""",
        validator = strict_range,
        values = [-99, 10],
        )

    level_mode = Instrument.control(
        "SOUR:POW:LEV:MODE?",
        "SOUR:POW:LEV:MODE %s",
        """A string property controlling the output attenuator and linearity mode,
        Possible selections are NORM, LOWN, CONT and LOWD""",
        validator = strict_discrete_set,
        values = ["NORM","LOWN","CONT","LOWD"]
        )

    rf_out = Instrument.control(
        "SOUR:POW:STAT?",
        "SOUR:POW:STATE %s",
        """ A bool property that controls the status of the RF-output,
        False => RF-output disabled,
        True => RF-output enabled
        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    #TODO add SOUR:TEL:IMOD (3.6.6.3 Intermodulation subsystem)

    #SOUR:TEL:MOD:COD (3.6.6.4)
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
        "SOUR:TEL:MOD:COD:MOD:DEGR %d",
        """ A int property that controls the fmodulation degree of the identification of the coder
        valid range 0 .. 0.9
        """,
        validator = strict_range,
        values=[0, 0.9],
        )

    coder_pilot_frequency = Instrument.control(
        "SOUR:TEL:MOD:COD:PIL:FREQ?",
        "SOUR:TEL:MOD:COD:PIL:FREQ %d",
        """ A int property that controls the pilot frequency of the coder
        valid range 40 .. 60 kHz
        """,
        validator = strict_range,
        values=[5E4, 6E4],
        )

    coder_pilot_deviation = Instrument.control(
        "SOUR:TEL:MOD:COD:PIL:FREQ:DEV?",
        "SOUR:TEL:MOD:COD:PIL:FREQ:DEV %d",
        """ A int property that controls deviation of the pilot frequency of the coder
        valid range 1 .. 4 kHz
        """,
        validator = strict_range,
        values=[1E3, 4E3],
        )

    #SOUR:TEL:MOD:EXT (3.6.6.5)
    external_modulation_power = Instrument.control(
        "SOUR:TEL:MOD:EXT:POW?",
        "SOUR:TEL:MOD:EXT:POW %d",
        """ A int property that controls the setting for the external modulator output power
        valid range -7..0 dBm
        """,
        validator = strict_range,
        values=[-7, 0],
        )

    external_modulation_frequency = Instrument.control(
        "SOUR:TEL:MOD:EXT:FREQ?",
        "SOUR:TEL:MOD:EXT:FREQ %d",
        """ A int property that controls the setting for the external modulator output power
        valid range 32 .. 46 MHz
        """,
        validator = strict_range,
        values=[32e6, 46e6],
        )

    #TODO NICAM system (3.6.6.6)
    #TODO SOUND (3.6.6.7)

    #Modulation (3.6.6.8)
    modulation_source = Instrument.control(
        "SOUR:MOD:SOUR?",
        "SOUR:MOD:SOUR %s",
        """ A bool property for the modulation source selection,
        False => Internal modulator is used,
        True => External external is used
        """,
        validator = strict_discrete_set,
        values={False:"INT", True:"EXT"},
        map_values = True,
        )

    modulation = Instrument.control(
        "SOUR:MOD:STAT?",
        "SOUR:MOD:STATE %s",
        """ A bool property that controls the modulation status,
        False => modulation disabled,
        True => modulation enabled
        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    #TODO VISION subsystem (3.6.6.9)

    #Television subsystem (3.6.6.10)
    lower_sideband = Instrument.control(
        "SOUR:TEL:SID?",
        "SOUR:TEL:SID %s",
        """ A bool property that controls the use of the lower sideband,
        False => upper sideband,
        True => lower sideband
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
        MONO,PIL (Pilot+mono),BTSC, STEReo, DUAL, NIC (nicam + mono)
        """,
        validator = strict_discrete_set,
        values=["MONO","PIL","BTSC","STER","DUAL","NIC"],
        )

    TV_standard = Instrument.control(
        "SOUR:TEL:STAN?",
        "SOUR:TEL:STAN %s",
        """ A string property that controls the type of video standard,
        Possible values are:
        BG, DK, I, K1, L, M, N
        """,
        validator = strict_discrete_set,
        values=["BG","DK","I","K1","L","M","N"],
        )

    TV_country = Instrument.control(
        "SOUR:TEL:STAN:COUN?",
        "SOUR:TEL:STAN:COUN %s",
        """ A string property that controls the country specifics of the video/sound system to be used,
        Possible values are:
        BG_General, DK_General, I_General, L_General, GERMany, BELGium, NETHerlands
        FINland, AUSTralia, BG_Tg, DENMark, NORWay, SWEDen, GUS, POLAND1, POLAND2,
        HUNGary, CHECho, CHINA1, CHINA2 , GREatbritain, SAFRica, FRANce, USA,
        KORea , JAPan, CANada, SAMerica
        """,
        validator = strict_discrete_set,
        values=["BG_G", "DK_G", "I_G", "L_G", "GERM","BELG", "NETH",
        "FIN", "AUST", "BG_T", "DENM", "NORW", "SWED", "GUS", "POLAND1", "POLAND2",
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
        valid range 0...32767
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
        False => beeper disabled,
        True => beeper enabled
        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    display_update = Instrument.control(
        "SYST:DISP:UPDATE:STATE?",
        "SYST:DISP:UPDATE:STATE %s",
        """ A bool property that controls the status of the displayed values ,
        False => No infomation on display during remote operation
        True => infomation shown on display
        """,
        validator = strict_discrete_set,
        values={False:0, True:1},
        map_values = True,
        )

    gpib_address = Instrument.control(
        "SYST:COMM:GPIB:ADDR?",
        "SYST:COMM:GPIB:ADDR %d",
        """ A int property that controls the GPIB address of the unit,
        valid range = 0..30
        """,
        validator = strict_range,
        values=[0, 30],
        )

    remote_interfaces = Instrument.control(
        "SYST:COM:REM?",
        "SYST:COM:REM %s",
        """A string property controlling the selection of interfaces for remote control,
        Possible selections are OFF, GPIB, SER and BOTH""",
        validator = strict_discrete_set,
        values = ["OFF","GPIB","SER","BOTH"]
        )

    ser_baud = Instrument.control(
        "SYST:COMM:SER:BAUD?",
        "SYST:COMM:SER:BAUD %g",
        """ A int property that controls the serial communication speed ,
        Possible values are: 110,300,600,1200,4800,9600,19200
        """,
        validator = strict_discrete_set,
        values=[110,300,600,1200,4800,9600,19200],
        )

    set_bits = Instrument.control(
        "SYST:COMM:SER:BITS?",
        "SYST:COMM:SER:BITS %g",
        """ A int property that controls the number of bits used in serial communication,
        Possible values are: 7 or 8
        """,
        validator = strict_discrete_set,
        values=[7,8],
        )

    ser_pace = Instrument.control(
        "SYST:COMM:SER:PACE?",
        "SYST:COMM:SER:PACE %s",
        """ A string property that controls the serial handshake type used in serial communication,
        Possible values are: NONE, XON, ACK (HW w/ RTS&CTS)
        """,
        validator = strict_discrete_set,
        values=["NONE","XON","ACK"],
        )

    ser_parity = Instrument.control(
        "SYST:COMM:SER:PAR?",
        "SYST:COMM:SER:PAR %s",
        """ A string property that controls the parity type used for serial communication ,
        Possible values are:
        NONE, EVEN, ODD, ONE (parity bit fixed to 1), ZERO (parity bit fixed to 0)
        """,
        validator = strict_discrete_set,
        values=["NONE","EVEN","ODD","ONE","ZERO"],
        )

    ser_stopbits = Instrument.control(
        "SYST:COMM:SER:SBIT?",
        "SYST:COMM:SER:SBIT %g",
        """ A int property that controls the number of stop-bits used in serial communication,
        Possible values are: 1 or 2
        """,
        validator = strict_discrete_set,
        values=[1,2],
        )


    scale_volt = Instrument.control(
        "UNIT:VOLT?",
        "UNIT:VOLT %s",
        """ A string property that controls the unit to be used for voltage entries on the unit,
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
                errmsg = "R&S SFM: %s: %s" % (err[0],err[1])
                log.error(errmsg + '\n')
            else:
                break
