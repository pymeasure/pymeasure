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

"""
Implementation of an interface class for ThermoStream® Systems devices.

Authors:
    - Markus Roeleke (markus.roeleke@bosch.com)

Reference Document for implementation:

ATS-515/615, ATS 525/625 & ATS 535/635 ThermoStream® Systems
Interface & Applications Manual
Revision E
September, 2019

Here the list of NOT implemented cmds:

Command      | imp | Description
#############+#####+#################################################################
*TST?        | no  | Self test (dummy, always returns 0, meaning “passed”).
-------------+-----+-----------------------------------------------------------------
*OPC         | no  | Not implemented
*OPC?        |     | 
-------------+-----+-----------------------------------------------------------------
*WAI         | no  | Not implemented
-------------+-----+-----------------------------------------------------------------
!            | no  | Device clear – clears the serial communications subsystem. The
             |     | System echos back the “!” when the command has completed. If the
             |     | “!” response is not received, the command should be retried.
             |     | NOTE: This command is sent as a single character (no line feed
             |     | terminator), and should never otherwise appear in a string sent to
             |     | the System.
-------------+-----+-----------------------------------------------------------------
^            | no  | The System sends a “^” as a service request (SRQ) indicator in
             |     | serial mode.
             |     | NOTE: The “^” character never otherwise displays in a response
             |     | string, and is sent as a single character.
-------------+-----+-----------------------------------------------------------------
"""

from pymeasure.instruments.instrument import Instrument
from pymeasure.instruments.validators import *
from enum import Enum
import time

import functools

GLOBAL_DELAY_FOR_CMD_EXEC = 0.05

def wait_for_cmd_exec(func):
    @functools.wraps(func)
    def wait_after_cmd(*args, **kwargs):
        val = func(*args, **kwargs)
        time.sleep(GLOBAL_DELAY_FOR_CMD_EXEC)
        return val
    return wait_after_cmd

Instrument.setting = wait_for_cmd_exec(Instrument.setting)
Instrument.control = wait_for_cmd_exec(Instrument.control)
Instrument.measurement = wait_for_cmd_exec(Instrument.measurement)


class StandardEventStatusCode(Enum):
    POWER_ON               = 128 # bit 7 – power on – not used
    USER_REQUEST           = 64  # bit 6 – user request -- not used
    COMMAND_ERROR          = 32  # bit 5 – command error (cme)
    EXECUTION_ERROR        = 16  # bit 4 – execution error (exe)
    DEVICE_DEPENDENT_ERROR = 8   # bit 3 – device dependent error (dde)
    QUERY_ERROR            = 4   # bit 2 – query error (qye)
    REQUEST_CONTROL        = 2   # bit 1 – request control -- not used
    OPERATION_COMPLETE     = 1   # bit 0 – operation complete -- not implemented


class TemperatureStatusCode(Enum):
                                 # bit 7 –- not used
                                 # bit 6 -- not used
    CYCLING_STOPPED        = 32  # bit 5 -- cycling stopped("stop on fail" signal was received)
    END_OF_ALL_CYCLES      = 16  # bit 4 -- end of all cycles
    END_OF_ONE_CYCLE       = 8   # bit 3 -- end of one cycle
    END_OF_TEST            = 4   # bit 2 -- end of test (test time has elapsed)
    NOT_AT_TEMPERATURE     = 2   # bit 1 -- not at temperature
    AT_TEMPERATURE         = 1   # bit 0 -- at temperature (soak time has elapsed)


class ErrorCode(Enum):
                                            # bit 15 – reserved
    NO_DUT_SENSOR_SELECTED         = 16384  # bit 14 – no DUT sensor selected
                                            # bit 13 – reserved
    BVRAM_FAULT                    = 4096   # bit 12 – BVRAM fault
    NVRAM_FAULT                    = 2048   # bit 11 – NVRAM fault
    NO_LINE_SENSE                  = 1024   # bit 10 – No Line Sense
    FLOW_SENSOR_HARDWARE_ERROR     = 512    # bit 9  – flow sensor hardware error
                                            # bit 8  – reserved
    INTERNAL_ERROR                 = 128    # bit 7  – internal error
                                            # bit 6  – reserved
    AIR_SENSOR_OPEN                = 32     # bit 5  – air sensor open
    LOW_INPUT_AIR_PRESSURE         = 16     # bit 4  – low input air pressure
    LOW_FLOW                       = 8      # bit 3  – low flow
                                            # bit 2  – reserved
    AIR_OPEN_LOOP                  = 2      # bit 1  – air open loop
    OVERHEAT                       = 1      # bit 0  – overheat


class TemptronicBase(Instrument):    
    """Represent the TemptronicATSXXX instruments.

    Examples
    -------
    Instantate a temptronic thermostream, define a temperature force
    operation and force 100 degC.
        
    >>> from pymeasure.instruments.temptronic import TemptronicATS525
    >>> ts =  TemptronicATS525("ASRL6::INSTR")   
    >>> ts.configure(temp_window=5, dut_type='T', soak_window=30)
    >>> ts.set_temperature(100)
    
    
    """ 

    remote_mode = Instrument.setting(
        "%s",
        """remote mode
        
        remote_mode = True -> Go into remote mode – the System touch screen controls are
        disabled, but a “Return to local” button appears.
        NOTE: When in remote mode, the touch screen controls are
        disabled each time the System receives a command.
        """,
        validator=strict_discrete_set,
        values={True:"%RM", False:"%GL"},
        map_values=True
        )

    maximum_test_time = Instrument.control(
        "TTIM?", "TTIM %g",
        """Set or get maximum allowed test time
        
        Set the maximum allowable test time.
        maximum_test_time = nnnn -- where nnnn is 0-9999 seconds
        NOTE: Setting a test time prevents the System from staying at one
        setpoint forever during cycling if a NEXT command or MCT
        interface “end of test” pulse is not received.
        """,
        validator=truncated_range,
        values=[0, 9999]
        )

    dut_mode = Instrument.control(
        "DUTM?", "DUTM %g",
        """Turn DUT mode on or off.

        dut_mode = 'OFF' -- off (air control)
        dut_mode = 'ON' -- on (DUT control)
        Read DUT mode on/off state.
        NOTE: The DUT mode state also appears as a bit in AUXC?.
        """,
        validator=strict_discrete_set,
        values={'ON':1, 'OFF':0},
        map_values=True
        )

    dut_type = Instrument.control(
        "DSNS?", "DSNS %g",
        """Set or read the DUT sensor type.

        dut_type = None (no DUT sensor)
        dut_type = 'T'  (type T thermocouple)
        dut_type = 'K'  (type K thermocouple)
        """,
        validator=strict_discrete_set,
        values={None:0, 'T':1, 'K':2},
        map_values=True
        )

    dut_constant = Instrument.control(
        "DUTC?", "DUTC %g",
        """Set the device thermal constant.

        DUTC nnn -- where nnn is nominally 100 but can range from 20 -
        500.
        NOTE: Use a higher number for a higher mass device, and to
        reduce the amount of overshoot. A lower number may cause some
        overshoot, but may also reduce the transition time.
        """,
        validator=truncated_range,
        values=[20,500]
        )

    head = Instrument.control(
        "HEAD?", "HEAD %s",
        """Raise or lower the test head (same as STND).

        head = 'down' (put head down)
        head = 'up'   (put head up)
        NOTE: Sending this command when the head is locked will NOT
        cause an error, but the head will not actually move.
        Read the up/down state of the test head.
        NOTE: The HEAD state also appears as a bit in AUXC?.
        """,
        validator=strict_discrete_set,
        values={'up':0, 'down':1},
        map_values=True
        )

    enable_air_flow = Instrument.setting(
        "FLOW %g",
        """Turn the main nozzle air flow on or off.
        enable_air_flow = True  (air flow on)
        enable_air_flow = False (air flow off)
        """,
        validator=strict_discrete_set,
        values={0,1,True,False}
        )

    temperature_limit_air_low = Instrument.control(
        "LLIM?", "LLIM %g",
        """lower air temperature limit.
        
        Set or get the lower air temperature limit.
        LLIM nnn -- where nnn is -99 to +25 °C
        NOTE: LLIM limits the minimum air temperature in both air and
        DUT control modes. Additionally, an “out of range” error generates
        if a setpoint is less than this value.
        
        """,
        validator=truncated_range,
        values=[-99, 25]
        )

    temperature_limit_air_high = Instrument.control(
        "ULIM?", "ULIM %g",
        """upper air temperature limit.
        
        Set or get the upper air temperature limit.
        ULIM nnn -- where nnn is 25 to 225 °C.
        NOTE: ULIM limits the maximum air temperature in both air and
        DUT control modes. Additionally, an “out of range” error generates
        if a setpoint exceeds this value.
        """,
        validator=truncated_range,
        values=[25, 225]
        )

    temperature_limit_air_dut = Instrument.control(
        "ADMD?", "ADMD %g",
        """Air to DUT limit.
        
        Set the air-to-DUT maximum difference.
        ADMD nnn -- where nnn is 10 - 300 °C in 1 degree increments.        
        """,
        validator=truncated_range,
        values=[10,300]
        )

    temperature_setpoint = Instrument.control(
        "SETP?", "SETP %g",
        """Set or get selected setpoint’s temperature
        
        Set the currently selected setpoint’s temperature.
        SETP nnn.n -- where nnn.n is –99.9 to 225.0 °C.
        NOTE: values entered must be with in the ULIM (the upper limit)
        and LLIM (the lower limit).
        """,
        validator=truncated_range,
        values=[-99.9, 225]
        )

    temperature_setpoint_window = Instrument.control(
        "WNDW?", "WNDW %g",
        """Setpoint’s temperature window
        
        Set the currently selected setpoint’s temperature window.
        WNDW n.n -- where n.n is 0.1 - 9.9 °C
        NOTE: The window is the maximum positive or negative deviation
        from the temperature setpoint allowable for an “at temperature”
        condition.
        """,
        validator=truncated_range,
        values=[0.1, 9.9]
        )

    temperature_soak_time = Instrument.control(
        "SOAK?", "SOAK %g",
        """
        Set the soak time for the currently selected setpoint.
        SOAK nnnn – where nnnn is 0 – 9999 seconds.
        """,
        validator=truncated_range,
        values=[0.0,9999]
        )

    temperature = Instrument.measurement(
        "TEMP?",
        """ current main temperature.
        
        Read the main temperature, in 0.1 °C increments.
        NOTE: This query returns air temperature when in air-control
        mode, or DUT temperature when in DUT-control mode.
        A returned value of greater than 400 degrees indicates an invalid
        temperature reading.
        """
        )

    temperature_condition_status_code = Instrument.measurement(
        "TECR?",
        """ temperature condition status register.
        
        bit 7 –- not used
        bit 6 -- not used
        bit 5 -- cycling stopped ("stop on fail" signal was received)
        bit 4 -- end of all cycles
        bit 3 -- end of one cycle
        bit 2 -- end of test (test time has elapsed)
        bit 1 -- not at temperature
        bit 0 -- at temperature (soak time has elapsed)
        """,
        validator=truncated_range,
        values=[0,255]
        )

    set_point_number = Instrument.control(
        "SETN?", "SETN %g",
        """Select a setpoint to be the current setpoint.
        SETN nn -- where n is 0 – 17 when on the Cycle screen.
        or
        SETN n – where n is 0 to 2 when on the Operator screen 
        (0=hot, 1=ambient, 2=cold).
        NOTE: Use *RST to reset (force) the System to the Cycle screen.
              Use RSTO to reset (force) the System to the Operator screen.
        NOTE: SETN arguments 0-11 correspon
        """,
        validator=truncated_range,
        values=[0,17]
        )

    standard_event_status_code = Instrument.measurement(
        "%S?",  # same as "*ESR?"
        """Read the standard event status register.

        bit 7 – power on – not used
        bit 6 – user request -- not used
        bit 5 – command error (cme)
        bit 4 – execution error (exe)
        bit 3 – device dependent error (dde)
        bit 2 – query error (qye)
        bit 1 – request control -- not used
        bit 0 – operation complete -- not implemented
        NOTE: The above bits are latched, and are automatically cleared
        when the register is read.
        """,
        validator=truncated_range,
        values=[0,255]
        )

    standard_event_status_mask = Instrument.control(
        "ESE?", "ESE %g",
        """Read the standard event status register.

        bit 7 – power on – not used
        bit 6 – user request -- not used
        bit 5 – command error (cme)
        bit 4 – execution error (exe)
        bit 3 – device dependent error (dde)
        bit 2 – query error (qye)
        bit 1 – request control -- not used
        bit 0 – operation complete -- not implemented
        NOTE: The above bits are latched, and are automatically cleared
        when the register is read.
        """,
        validator=truncated_range,
        values=[0,255]
        )

    service_request_mask = Instrument.control(
        "SRE?", "SRE %g",
        """Set the service request enable (mask) register.

        SRE nnn -- where nnn is 0 – 255
        bit 7 – ready
        bit 6 – request for service (RQS)
        bit 5 – standard event status (ESB) summary bit
        bit 4 – message available (MAV) (always 0 for RS-232)
        bit 3 – temperature event (TESR) summary bit
        bit 2 – device specific error (EROR) summary bit
        bit 1 – not used (always 0)
        bit 0 – not used (always 0)
        NOTE: See <serial poll> for the meaning of each bit in the mask.
        Read the service request enable (mask) register.
        """,
        validator=truncated_range,
        values=[0,255]
        )

    local_lockout = Instrument.setting(
        "%LL",
        """Local lockout – the System touch screen controls are disabled, and
        no “Return to local” button appears on the panel.
        """
        )


    system_current = Instrument.measurement(
        "AMPS?",
        """Read the system’s current draw (amperage).
        """,
        )


    auxiliary_condition_code = Instrument.measurement(
        "AUXC?",
        """Read the auxiliary condition register.

        bit 10 – reserved
        bit 9 – ramp mode
        bit 8 – Manual Mode= 1, Program= 0
        bit 7 – reserved
        bit 6 – ready for operation = 1, startup sequence = 0
        bit 5 – flow on = 1, flow off = 0
        bit 4 – DUT mode = 1, air-control mode = 0
        bit 3 – heat only mode = 1, compressor on =0
        bit 2 – head up = 1, head down = 0
        bit 1 – reserved
        bit 0 – reserved
        """,
        validator=truncated_range,
        values=[0, 1023]
        )
 
    copy_active_setup_file = Instrument.setting(
        "CFIL %g",
        """Local lockout – the System touch screen controls are disabled, and
        no “Return to local” button appears on the panel.
        """,
        validator=strict_range,
        values=[1, 12]
        )

    clear_errors = Instrument.setting(
        "CLER",
        """Local lockout – the System touch screen controls are disabled, and
        no “Return to local” button appears on the panel.
        """
        )

    compressor_enable = Instrument.setting(
        "COOL %g",
        """Turn the compressor on or off.
        compressor_enable = True (turn the compressor on)
        compressor_enable = False (turn the compressor off)
        """,
        validator=strict_discrete_set,
        values={0,1,True,False}
        )

    total_cycle_count = Instrument.control(
        "CYCC?", "CYCC %g",
        """Set the cycle count.

        CYCC nnnn -- where nnnn is the number (1 - 9999) of cycles to do.
        Read the number of cycles to do.

        total_cycle_count = nnnn (start cycling)
        total_cycle_count = 0    (stop cycling)
        NOTE: When all cycles have been completed or when cycling was
        stopped on failure, it is necessary to send a CYCL 0 command to
        reset the system.
        """,
        validator=truncated_range,
        values=[0, 9999]
        )

    cycling_enable = Instrument.setting(
        "CYCL %g",
        """CYCL Start/stop cycling.
        cycling_enable = True  (start cycling)
        cycling_enable = False (stop cycling)
        NOTE: When all cycles have been completed or when cycling was
        stopped on failure, it is necessary to send a CYCL 0 command to
        reset the system.
        Read the cycle number (current value if cycling, last value if not).
        NOTE: If Version 1 compatibility mode is enabled, CYCL? returns
        the number of fully completed cycles.
        """,
        validator=strict_discrete_set,
        values={0,1,True,False}
        )

    current_cycle_count = Instrument.measurement(
        "CYCL?",
        """Read the system’s current draw (amperage).
        """,
        )

    error_code = Instrument.measurement(
        "EROR?",
        """Read the device-specific error register (16 bits).

        bit 15 – reserved
        bit 14 – no DUT sensor selected
        bit 13 – reserved
        bit 12 – BVRAM fault
        bit 11 – NVRAM fault
        bit 10 – No Line Sense
        bit 9  – flow sensor hardware error
        bit 8  – reserved
        bit 7  – internal error
        bit 6  – reserved
        bit 5  – air sensor open
        bit 4  – low input air pressure
        bit 3  – low flow
        bit 2  – reserved
        bit 1  – air open loop
        bit 0  – overheat
        """,
        validator=truncated_range,
        values=[0, int(2**16-1)]
        )

    nozzle_air_flow_rate = Instrument.measurement(
        "FLWR?",
        """Read the measured main nozzle air flow rate, in scfm.

        NOTE: This query and FLWR? are identical.
        """
        )

    main_air_flow_rate = Instrument.measurement(
        "FLRL?",
        """Read the measured main nozzle air flow rate, in liters/sec.
        """
        )

    learn_mode = Instrument.control(
        "LRNM?", "LRNM %g",
        """Turn DUT automatic tuning (learning) on or off.

        learn_mode = False – off (control DUT with current DUT control parameters)
        learn_mode = True – automatic tuning on
        NOTE: LRNM 0 is equivalent to DTYP 0. LRNM 1 is equivalent
        to DTYP 1.
        """,
        validator=strict_discrete_set,
        values={0,1,True,False}
        )

    ramp_rate = Instrument.control(
        "RAMP?", "RAMP %g",
        """Set the ramp rate for the currently selected setpoint, in °C per minute.

        RAMP nn.n – where nn.n is 0 to 99.9 in 0.1 °C per minute steps.
        or
        RAMP nnnn – where nnnn is 100 to 9999 in 1 °C per minute steps.
        Read the setting of RAMP.
        """,
        validator=strict_discrete_set,
        values={i/10 for i in range(1000)} | {i for i in range(100, 10000)}
        )

    dynamic_temperature_setpoint = Instrument.measurement(
        "SETD?",
        """Read the dynamic temperature setpoint.
        NOTE: This value changes during a temperature ramp to reflect the
        instantaneous value at the time the query is executed.
        """
        )

    load_setup_file = Instrument.setting(
        "SFIL %g",
        """loads setup file SFIL n where n is 1 - 12.
        """,
        validator=strict_range,
        values=[1, 12]
        )

    enable_temperature_event_status = Instrument.control(
        "TESE?", "TESE %g",
        """ Set the temperature event status enable (mask) register.
        TESE nnn -- where nnn is 0 – 255
        
        bit 7 - not used
        bit 6 - not used
        bit 5 - stopped cycling ("stop on fail" signal was received)
        bit 4 - end of all cycles
        bit 3 - end of one cycle
        bit 2 - end of test (test time has elapsed)
        bit 1 - not at temperature
        bit 0 - at temperature (soak time has elapsed) 

        NOTE: See TESR? for the meaning of each bit in the mask.
        Read the temperature event status enable (mask) register.
        """,
        validator=strict_range,
        values=[0, 255]
        )

    temperature_event_status = Instrument.measurement(
        "TESR?",
        """ temperature event status register.
        
        bit 7 - not used
        bit 6 - not used
        bit 5 - stopped cycling ("stop on fail" signal was received)
        bit 4 - end of all cycles
        bit 3 - end of one cycle
        bit 2 - end of test (test time has elapsed)
        bit 1 - not at temperature
        bit 0 - at temperature (soak time has elapsed) 
        """,
        validator=strict_range,
        values=[0, 255]
        )

    air_temperature = Instrument.measurement(
        "TMPA?",
        """Read air temperature, in 0.1 °C increments.

        NOTE: This query always returns the air temperature, whether in
        air or DUT control modes.
        """
        )

    dut_temperature = Instrument.measurement(
        "TMPD?",
        """Read DUT temperature, in 0.1 °C increments.
        
        NOTE: This query always returns the DUT temperature, whether in
        air or DUT control modes.
        """
        )

    mode = Instrument.measurement(
        "WHAT?",
        """Returns an integer indicating what the system is doing at the time the query is processed.
        
        5 = on Operator screen (manual mode)
        6 = on Cycle screen (program mode)
        """,
        values={'manual' : 5, 
                'program'  : 6},
        map_values=True
        )

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, "Temptronic ATS-525 Thermostream", **kwargs)

    def reset(self):
        """Reset (force) the System to the Operator screen.
        
        NOTE: Any device-specific errors are reset. Setpoint number 1
        (Ambient) becomes the active setpoint.
        """
        self.write("RSTO")
    
    def enter_cycle(self):
        """Enter Cycle.
        RMPC 1 = enter cycle
        """
        self.write("RMPC 1")

    def enter_ramp(self):
        """Enter Ramp.
        RMPS 1 = enter ramp
        """
        self.write("RMPS 1")

    def next_setpoint(self):
        """Step to the next setpoint during temperature cycling.

        NOTE: Stepping occurs whether or not the device is at temperature.
        NEXT causes an error if the system is not in cycling mode.
        """
        self.write("NEXT")

    def configure(self, temp_window=1, dut_type='T', soak_time=30, dut_constant=350, temp_limit_air_low=-60, temp_limit_air_high=220, temp_limit_air_dut=50):
        """configure a new temperature to be forced.

        Parameters
        ----------
            
        dut_type : string
            string indicating which dut type to use
            ''  : no dut,
            'T' : T-DUT,
            'K' : K-DUT
        
        soak_time : float
            soak time before settling is indicated
        
        soak_window : float
            soak window size
        
        dut_constant : float
            time constant of dut, higher values indicate higher thermal mass
        
        temp_limit_air_low: float
            minimum flow temperature limit
        
        temp_limit_air_high: float
            maximum flow temperature limit
        
        temp_limit_air_dut: float
            maximum allowed difference between DUT and Flow temperature

        Returns
        -------
        none
          

        Examples
        -------
        
        configure a temperature force operation with T type thermocouple
        and 30 second soak time intervall,
        all other parameters are set to their pre-defined default
        
        >>> ts.conf_set_temp(temp_window=5, dut_type='T', soak_window=30)
        """
        self.maximum_test_time = 3600*5   # max 5 houre test time
        #sent dut type
        self.dut_type=dut_type
        #temperature window
        self.temperature_setpoint_window = temp_window        
        #temperature limit low
        self.temperature_limit_air_low = temp_limit_air_low   
        #temperature limit high
        self.temperature_limit_air_high = temp_limit_air_high    
        self.dut_mode = 'ON'
        self.dut_constant = dut_constant
        self.temperature_limit_air_dut = temp_limit_air_dut
        self.temperature_soak_time = soak_time
        
    def set_temperature(self, set_temp):
        """sweep to a specified.

        Parameters
        ----------
        set_temp : float
            target temperature for DUT
            
        Returns
        -------
        none

        Examples
        -------
        
        configure a default force temperature operation and sweep to 100 degC
        
        >>> ts.conf_set_temp()
        >>> ts.set_temp(100)
                     
        """
        if self.mode == 'manual':
            if set_temp <= 20:
                self.set_point_number = 2 # cold
            elif set_temp < 30:
                self.set_point_number = 1 # ambient
            elif set_temp >= 30:
                self.set_point_number = 0 # hot
            else:
                raise ValueError(f"Temperature {set_temp} is impossible to set!")

        self.temp_set_point=set_temp 

    def wait_for_settling(self, time_limit=300, log=False):
        """sweep to a specified.

        Parameters
        ----------
        set_temp : float
            target temperature for DUT
        
        time_limit : float
            set the maximum blocking time within thermostream has to settle.
            Script execution is blocked until either thermostream has settled
            or time_limte has been exceeded.
        
        log : boolean
            show polling progress in command line
            
        Returns
        -------
        none

        Examples
        -------
        
        configure a default force temperature operation and sweep to 100 degC.
        Stop script execution until temperature has settled or if it runs longer
        than 150 s and use logging
        
        >>> ts.conf_set_temp()
        >>> ts.set_temp_wait_settling(100,150)
        temp_set= 100.0 deg, temp = 27.2 deg, time elapsed =   10 s, status = not at temperature             
        """
        # delay (thermostream firmware issue)
        # force set_temp
        time.sleep(1)
        t = 0
        while( not self.at_temperature()): #assert at temperature
            time.sleep(1)
            t += 1
            if log == True:
                print(f"temp_set= {self.temperature_setpoint:4.1f} deg,",
                      f"temp = {self.temperature:4.1f} deg,",
                      f"time elapsed = {t:4.0f} s,",
                      f"status = {self.temperature_event_status}")
                
            if t > time_limit:
                print('no settling achieved')
                break

    def stop(self):
        # shut down thermo stream
        self.enable_air_flow = 0
        self.remote_mode = False
        self.head = 'up'

    def start(self):
        self.remote_mode = True
        self.enable_air_flow = 1 # enable thermostream

    def cycling_stopped(self):
        """check if cycling has stopped.      
        """
        return self.temperature_condition_status_code & TemperatureStatusCode.CYCLING_STOPPED

    def end_of_all_cycles(self):
        """ check if cycling has stopped.
        """
        return self.temperature_condition_status_code & TemperatureStatusCode.END_OF_ALL_CYCLES

    def end_of_one_cycle(self):
        """ check if end of (at least) one cycle is done.
        """
        return self.temperature_condition_status_code & TemperatureStatusCode.END_OF_ONE_CYCLE

    def end_of_test(self):
        """ check if end of test is reached.
        """
        return self.temperature_condition_status_code & TemperatureStatusCode.END_OF_TEST

    def not_at_temperature(self):
        """ check if not (yet) at temperature.
        """
        return self.temperature_condition_status_code & TemperatureStatusCode.NOT_AT_TEMPERATURE

    def at_temperature(self):
        """ check if at temperature.
        """
        return self.temperature_condition_status_code & TemperatureStatusCode.AT_TEMPERATURE
    
    def __enter__(self):
        return self

    def __exit__(self):
        self.stop()
