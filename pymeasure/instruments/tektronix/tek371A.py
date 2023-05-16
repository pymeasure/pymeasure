#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
# FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import logging
import time
from enum import IntFlag

from pyvisa import constants as pyvisa_constants

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range
from pymeasure.instruments.validators import strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Tektronix371A(Instrument):
    """ Represents the Tektronix Curve Tracer model 371A
    and provides a high-level interface for interacting with
    the instrument using the SCPI command set for getting the characteristic curves
    of several power electronics devices like diodes, IGBTs, MOSFETs, etc...

    Typically, a set of curve got from the instrument will be about 4122 bytes long,
    with most of the bytes being binary-coded numbers.
    Thus, most of the string of data is not directly readable, but must be interpreted by
    the controller. An example might look like this. CURVE CURVID:”INDEX 9”,%NNXXYYXXYY . .
    . XXYYC This example breaks down as follows. It starts with an ASCII string of 25
    characters: CURVE CURVID:”INDEX 9”,% This is followed by a series of binary bytes. The
    first of these is two bytes giving the number of data bytes to follow, plus one (
    typically 4097): NN Then come the 4096 data bytes. Each of the 1024 data points on the
    curve is represented by four bytes, 2 for the 10 bits of the X coordinate and 2 for the
    10 bits of the Y coordinate: XXYYXXYY . . . XXYY And finally there is one byte which is
    the checksum for the preceding 4098 data bytes.

    The first XXYY of the 1024 points is the first point taken whe we execute the sweep.
    Last point should be the coordinates 0,0.
    XXYY is coordinate point. Thus, we have to translate it for getting electrical values.

    Format of the curve data ASCII HEAD (25b) + NN (2b) + XXYYXXYY......XXYY (points to
    read 1024 points typ) + C (checksum 1b) + EOL

    Curves data needs information to be interpreted, in our case that information is called preamble
    The preamble is a string of ASCII letters, numerals, and punctuation.
    Each character is represented by one byte.
    Preambles are necessary to interpret the numeric information in the curve data that
    follows them. Within a preamble, 26 parameters are specified.
    The first ten are unique to the 371B curve tracer and are included as a sub-string linked
    to the WFID: label. The other 16 parameters include ten that have fixed values and
    six that vary with the particular data sent.
    Within the WFID: sub-string the parameters are separated by slashes, while the entire
    sub-string is delimited by a pair of double quote marks.
    Most of the WFID: string is rather strictly defined,
    with each parameter value being right justified in a fixed length field.
    An exception is the BGM value, which may vary in field length. The remainder of the
    preamble uses standard punctuation. A colon links each parameter label with its
    corresponding value and the individual label and value pairs are separated with commas.

    A complete preamble might look like this: WFMPRE WFID:”INDEX 3/VERT 500MA/ HORIZ 1V/STEP
    5V/OFFSET 0.00V/BGM 100mS/VCS 12.3/TEXT /HSNS VCE”, ENCDG:BIN, NR.PT:3,PT.FMT:XY,
    XMULT:+1.0E–2,XZERO:0,XOFF: 12,XUNIT:V,YMULT:+5.0E–3,YZERO:0,YOFF:12, YUNIT:A,BYT/ NR:2,
    BN.FMT:RP,BIT/NR:10,CRVCHK:CHKSMO,LN.FMT:DOT

    .. code-block:: python

    ct371A = Tektronix371A("GPIB0::23::INSTR")
    # COLLECTOR SUPPLY
    ct371A.cs_peakpower = 300
    ct371A.cs_polarity = "POS"
    ct371A.cs_collector_supply = 0
    # STEP GEN
    ct371A.stepgen_step_source_and_size = ("VOLTAGE", 5.0)
    ct371A.stepgen_number_steps = 0
    ct371A.set_stepgen_offset(0)
    # DISPLAY
    ct371A.diplay_store_mode = "STO"
    ct371A.display_horizontal_source_sensitivity = ("COLLECT", 1.0E-1)
    ct371A.display_vertical_source_sensitivity = ("COLLECT", 500.0E-3)
    ct371A.set_cursor_mode("DOT", 1)
    # MEASUREMENT
    ct371A.measure_mode = "REP"

    """

    ADC_NBITS = 10  # The number of bits of the Analog to Digital converter of the instrument
    COLLECTOR_SUPPLY_POLARITY_MODES = ["NPN", "POSitive", "PNP", "NEGative", "POS", "NEG"]
    COLLECTOR_SUPPLY_PEAKPOWER_VALUES = [3000, 300, 30, 3]  # in watts
    COLLECTOR_SUPLLY_RANGE = [0.0, 100.0]  # in % of max peak power
    HORIZONTAL_SOURCE_SET = ["STPgen", "STP", "COLlect", "COL"]
    VERTICAL_SOURCE_SET = ["COLlect", "COL"]
    STEP_GENERATOR_SOURCE_SET = ["VOLtage", "CURrent", "VOL", "CUR"]
    DISPLAY_VALID_STORE_MODES = ["NST", "STO", "NSTore", "STOre"]
    VALID_MEASUREMENT_MODES = ["REPeat", "REP", "SINgle", "SIN", "SWEep", "SWE", "SSWeep", "SSW"]
    VALID_CURSOR_MODES = ["OFF", "DOT", "LINE", "WINDOW"]
    # 0 is the beginning and 1023 is the end of the valid coordinates set
    VALID_V_H_COORDINATES_SET = [0, pow(2, ADC_NBITS) - 1]

    STEP_GENERATOR_VALID_VOLTAGE_STEP_SELECTIONS_VS_PEAKPOWER = \
        dict.fromkeys(
            [3000.0, 300.0, 30.0, 3.0, 0.3, 0.03], [0.2, 0.5, 1, 2, 5]
        )

    STEP_GENERATOR_VALID_CURRENT_STEP_SELECTIONS_VS_PEAKPOWER = \
        dict.fromkeys(
            [3000.0, 300.0], [1E-3, 2E-3, 5E-3, 1E-2, 20E-3, 50E-3, 0.1, 0.2, 0.5, 1, 2]
        )
    STEP_GENERATOR_VALID_CURRENT_STEP_SELECTIONS_VS_PEAKPOWER.update(
        dict.fromkeys(
            [30.0, 3.0, 0.3, 0.03],
            [1E-6, 2E-6, 5E-6, 1E-5, 20E-6, 50E-6, 100E-6, 200E-6, 500E-6, 1E-3, 2E-3]
        )
    )

    STEP_GENERATOR_VALID_STEP_SELECTIONS_FOR_STEP_SOURCE = \
        {
            "VOLTAGE": STEP_GENERATOR_VALID_VOLTAGE_STEP_SELECTIONS_VS_PEAKPOWER,
            "CURRENT": STEP_GENERATOR_VALID_CURRENT_STEP_SELECTIONS_VS_PEAKPOWER
        }

    STEP_GENERATOR_NUMBER_OF_STEPS_RANGE = [0, 5]

    HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_COLLECTOR_SOURCE = \
        {
            3000.0: [100E-3, 200E-3, 0.5, 1, 2, 5],
            300.0: [100E-3, 200E-3, 0.5, 1, 2, 5],
            30.0: [50, 100, 200, 500],
            3.0: [50, 100, 200, 500]
        }

    HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_STEPGEN_SOURCE = \
        dict.fromkeys(
            [3000, 300, 30, 3], [100E-3, 200E-3, 0.5, 1, 2, 5]
        )

    HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE = \
        dict.fromkeys(
            ["STP", "STPgen", "STPGEN"],
            HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_STEPGEN_SOURCE
        )

    HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE.update(
        dict.fromkeys(
            ["COL", "COLlect", "COLLECT"],
            HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_COLLECTOR_SOURCE
        )
    )

    VERTICAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_COLLECTOR_SOURCE = \
        {
            3000.0: [1, 2, 5, 10, 20, 50],
            300.0: [0.5, 1, 2, 5],
            30.0: [100E-6, 200E-6, 500E-6, 1E-3, 2E-3, 5E-3],
            3.0: [10E-6, 20E-6, 50E-6, 100E-6, 200E-6, 500E-6]
        }

    VERTICAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE = \
        dict.fromkeys(
            ["COL", "COLlect", "COLLECT"],
            VERTICAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_COLLECTOR_SOURCE
        )

    def __init__(self,
                 adapter,
                 name="Tektronix Curve Tracer model 371A",
                 query_delay=0.5,
                 write_delay=0.5,
                 timeout=5000,
                 **kwargs):
        super().__init__(
            adapter,
            name,
            write_termination="\n",
            read_termination="",
            send_end=True,
            includeSCPI=True,
            timeout=timeout,
            **kwargs
        )

        self.write_delay = write_delay
        self.query_delay = query_delay
        self.last_write_timestamp = 0.0
        self.srq_called = False

    # ############################################
    # # Tektronix Curve Tracer 371A SCPI commands.
    # ############################################

    id = Instrument.measurement(
        "ID?",
        """Measure the identification of the instrument (string) """,
        maxsplit=2,
        get_process=lambda r:
        ", ".join(r)
    )

    help = Instrument.measurement(
        "HELp?",
        """Measure the list of valid commands for the instrument.""",
        get_process=lambda r:
        "VALID COMMANDS AND QUERY HEADERS:\n" + " \n --> ".join(r)
    )

    front_panel_settings = Instrument.measurement(
        "SET?",
        """Measure the actual front-panel settings of the instrument.""",
        separator=";",
        get_process=lambda r:
        "FRONT PANEL SETINGS:\n" + "\n --> ".join(r)
    )

    #########################################################################
    # # COLLECTOR SUPPLY COMMANDS
    #########################################################################

    cs_breakers = Instrument.measurement(
        "CSOut?",
        """Measure the actual collector HIGH VOLTAGE and HIGH CURRENT breakers settings
        of the instrument.""",
        separator=" ",
        maxsplit=1,
        get_process=lambda r:
        r[1]
    )

    cs_polarity = Instrument.control(
        "CSPol?", "CSPol %s",
        """Control the collector supply polarity and mode.""",
        validator=strict_discrete_set,
        values=COLLECTOR_SUPPLY_POLARITY_MODES
    )

    cs_peakpower = Instrument.control(
        "PKPower?", "PKPower %s",
        """Control the collector supply peak power watts settings.""",
        validator=strict_discrete_set,
        values=COLLECTOR_SUPPLY_PEAKPOWER_VALUES,
        get_process=lambda r:
        float(r[1]) if isinstance(r, list)
        else float("".join(r.replace(" ", "")).replace("PKPOWER", ""))
    )

    cs_collector_supply = Instrument.control(
        "VCSpply?", "VCSpply %f",
        """Control the collector supply output level (from 0.0% to 100.0% in 0.1% increments).\n
        Values out of range or with more than one decimal will be ignored""",
        set_process=lambda x: round(x, 1),
        get_process=lambda r:
        float(r[1]) if isinstance(r, list)
        else float("".join(r.replace(" ", "")).replace("VCSPPLY", ""))
    )

    ################################################################################
    # # CRT READOUT TRANSFER COMMANDS
    # # Group of commands for reading the vertical and horizontal cursor parameters.
    ################################################################################

    crt_readout_h = Instrument.measurement(
        "REAdout? SCientific",
        """Measure the horizontal cursor reading in volts.""",
        get_process=lambda r:
        float(r[0].replace(" ", "").replace("READOUT", ""))
    )

    crt_readout_v = Instrument.measurement(
        "REAdout? SCientific",
        """Measure the vertical cursor reading in amperes (ohm or siemens for f line cursor).""",
        get_process=lambda r:
        float(r[1])
    )

    crt_text = Instrument.control(
        "TEXt?", 'TEXt "%s"',
        """Control the writing of a text on the display. No more than 24 characters is possible.""",
        get_process=lambda r:
        "".join(r.replace(" ", ""))
    )

    ###############################################################################
    # # CURSOR COMMANDS
    # # Group of commands for controlling the cursor on the display.
    ###############################################################################

    def set_cursor_mode(self, mode="", *args):
        """
        Control the cursor mode of the instrument
        :param mode: string which can be: "OFF", "DOT", "LINE" or "WINDOW"
        :param args: optional arguments used in "DOT", "LINE" and "WINDOW" modes.
        See Tektronix 371B user manual for more details.
        :return: None
        """
        uc_mode = mode.upper()
        if uc_mode not in Tektronix371A.VALID_CURSOR_MODES:
            raise ValueError(
                "Cursor mode must be one of the values:"
                + str(Tektronix371A.VALID_CURSOR_MODES)
            )

        if uc_mode == Tektronix371A.VALID_CURSOR_MODES[0]:  # OFF mode
            self.write("CURSor OFF")
            return

        # If there is no curve in the screen and only a point ( a dot) then the setting
        # will only accept one value equal due is considered the curve only have 1 point.
        # In that case, the cursor configuration only will change from OFF to DOT if
        # the command DOT 1 is sent, otherwise cursor configuration will remain in last state.
        # While cursor configuration is in OFF state, cursor readout will return nothing.
        if uc_mode == Tektronix371A.VALID_CURSOR_MODES[1]:  # DOT mode
            self.write("DOT " + str(args[0]))
            return

        if uc_mode == Tektronix371A.VALID_CURSOR_MODES[2]:  # LINE mode
            try:
                strict_range(args[0], Tektronix371A.VALID_V_H_COORDINATES_SET)
                strict_range(args[1], Tektronix371A.VALID_V_H_COORDINATES_SET)
            except Exception as exc:
                raise ValueError(
                    str(args[0])
                    + " is not a valid horizontal or vertical coordinate for the line cursor.\n"
                    + " Valid horizontal or vertical coordinate values are: "
                    + str(Tektronix371A.VALID_V_H_COORDINATES_SET)
                ) from exc

            self.write("LINe " + str(args[0]) + "," + str(args[1]))
            return

        if uc_mode == Tektronix371A.VALID_CURSOR_MODES[3]:  # WINDOW mode

            try:
                strict_range(args[0], Tektronix371A.VALID_V_H_COORDINATES_SET)
                strict_range(args[1], Tektronix371A.VALID_V_H_COORDINATES_SET)
                strict_range(args[2], Tektronix371A.VALID_V_H_COORDINATES_SET)
                strict_range(args[3], Tektronix371A.VALID_V_H_COORDINATES_SET)
            except Exception as exc:
                raise ValueError(
                    str(args[0])
                    + " is not a valid horizontal or vertical coordinate for the window cursor.\n"
                    + " Valid horizontal or vertical coordinate values are: "
                    + str(Tektronix371A.VALID_V_H_COORDINATES_SET)
                ) from exc

            self.write(
                "WINdow " + str(args[0]) + "," + str(args[1]) + "," + str(args[2]) + "," + str(
                    args[3]))
            return

    cursor_dot = Instrument.measurement(
        "DOT?",
        """Measure the cursor dot position.""",
        get_process=lambda r:
        float("".join(r.replace(" ", "")).replace("DOT", ""))
    )

    cursor_dot_hvalue = Instrument.measurement(
        "REAdout? SCientific",
        """Measure the vertical and horizontal cursor parameters.""",
        get_process=lambda r:
        float(r[0].removeprefix("READOUT").strip())
    )

    cursor_dot_vvalue = Instrument.measurement(
        "REAdout? SCientific",
        """Measure the vertical and horizontal cursor parameters.""",
        get_process=lambda r:
        float(r[1])
    )

    ###############################################################################
    # # DISPLAY COMMANDS
    # # Group of commands for controlling the status of the display.
    ###############################################################################

    diplay_store_mode = Instrument.control(
        "DISplay?", "DISplay %s",
        """Control the store mode of the display of the instrument.
        Valid Modes are: ["NST", "STO", "NSTore", "STOre"]""",
        validator=strict_discrete_set,
        values=DISPLAY_VALID_STORE_MODES,
        get_process=lambda r:
        r[2]
    )

    display_horizontal_source_sensitivity = Instrument.control(
        "HORiz?", "HORiz %s:%s",
        """Control the horizontal source (COLLECT O STPGEN) and
        its sensitivity (volt/div) for the horizontal axis on the display.\n
        Use example: instrument.display_horizontal_source_sensitivity = ("COLLECT", 1.0)
        Use example: instrument.display_horizontal_source_sensitivity will return ['COLLECT', 1.0]
        """,
        # e.g. if we want to configure the horizontal source and sensitivity as 'COLLECT' with
        # sensitivity equals to 1.0 volt/div then we will use the next expression:
        # instrument.display_horizontal_source_sensitivity = ("COLLECT", 1.0).\n After that,
        # if we want to ask the instrument for the actual display_horizontal_source_sensitivity,
        # the we will use the next expression: instrument.display_horizontal_source_sensitivity
        # and we should obtain a list as follow: ['COLLECT',1.0]. Parameters out ouf range will
        # have no effect.
        get_process=lambda r:
        ["".join(r.replace(" ", "")).replace("HORIZ", "").split(":", maxsplit=1)[0],
         float("".join(r.replace(" ", "")).replace("HORIZ", "").split(":")[1])]
    )

    display_vertical_source_sensitivity = Instrument.control(
        "VERt?", "VERt %s:%s",
        """Control the vertical source (COLLECT) and its sensitivity (A/div)
        for the vertical axis on the display.\n
        Use example: instrument.display_vertical_source_sensitivity = ("COLLECT", 1.0)
        Use example: instrument.display_vertical_source_sensitivity will return ['COLLECT', 1.0]
        """,
        # e.g. if we want to configure the vertical source and sensitivity as 'COLLECT' with
        # sensitivity equals to 1.0 A/div then we will use the next expression:
        # instrument.display_vertical_source_sensitivity = ("COLLECT", 1.0).\n After that,
        # if we want to ask the instrument for the actual display_vertical_source_sensitivity,
        # the we will use the next expression: instrument.display_vertical_source_sensitivity and
        # we should obtain a list as follow: ['COLLECT',1.0]. Parameters out ouf range will have
        # no effect.
        get_process=lambda r:
        ["".join(r.replace(" ", "")).replace("VERT", "").split(":", maxsplit=1)[0],
         float("".join(r.replace(" ", "")).replace("VERT", "").split(":")[1])]
    )

    #########################################################################
    # # STEP GENERATOR
    #########################################################################

    stepgen_output = Instrument.control(
        "STPgen?", "STPgen OUT:%s",
        """Control the instrument step generator output enable (boolean).\n
        After enable the stepgen_output (even if it was enable before)
        step generator parameters change.""",
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True,
        get_process=lambda r:
        r[0].split(":")[1] == 'ON' if isinstance(r, list)  # case stepgen output 'ON'
        else r.split(":")[1]
    )

    stepgen_number_steps = Instrument.control(
        "STPgen?", "STPgen NUMber:%d",
        """Control the instrument step generator number of steps (int).""",
        validator=strict_range,
        values=STEP_GENERATOR_NUMBER_OF_STEPS_RANGE,
        get_process=lambda r:
        int(r[1].split(":")[1]) if isinstance(r, list)  # case stepgen output 'ON'
        else r.split(":")[1]
    )

    stepgen_invert = Instrument.control(
        "STPgen?", "STPgen INVert:%s",
        """Control the instrument step generator invert option (boolean).""",
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True,
        get_process=lambda r:
        r[3].split(":")[1] == 'ON' if isinstance(r, list)  # case stepgen output 'ON'
        else r.split(":")[1]
    )

    stepgen_step_size_multiplier = Instrument.control(
        "STPgen?", "STPgen OFFset:%f",
        """Control the step multiplier value which is the offset (float).""",
        get_process=lambda r:
        float(r[2].split(":")[1]) if isinstance(r, list)  # case stepgen output 'ON'
        else r.split(":")[1]
    )

    stepgen_step_source_and_size = Instrument.control(
        "STPgen?", "STPgen %s:%s",
        """Control the step size and souce for the step generator (Amps or Volts per step).\n
        Use example: instrument.stepgen_step_source_and_size = ("VOLTAGE", 2.0)
        Use example: instrument.stepgen_step_source_and_size will return ['VOLTAGE', 2.0]
        """,
        # e.g. if we want to configure the step generator as voltage with step size equals to 2V
        # then we will use the next expression: instrument.stepgen_step_source_and_size = (
        # "VOLTAGE", 2.0).\n After that, if we want to ask the instrument for the step generator
        # source and size then we will use the next expression:
        # instrument.stepgen_step_source_and_size and we should obtain a list as follow:
        # ['VOLTAGE',2.0]. Parameters out ouf range will have no effect.
        get_process=lambda r:
        [r[5].split(":")[0], float(r[5].split(":")[1])] if isinstance(r, list)
        else r.split(":")[1]
    )

    @property
    def stepgen_offset(self):
        """
        Get the offset of the step generator of the instrument.
        :return: float containing the offset (volts or amps).
        """
        mult = self.stepgen_step_size_multiplier
        s_size = self.stepgen_step_source_and_size[1]
        invert = self.stepgen_invert
        abs_offset = mult * s_size
        return -abs_offset if invert else abs_offset

    @stepgen_offset.setter
    def stepgen_offset(self, offset):
        """
        Configure the offset of the step generator of the instrument
        changing the step size multiplier and invert param.
        :param offset: Will be a float valid between some valid range which depends on the step size
        and step generator source. The instrument only will consider increments of the 10%
        of the step size, other values will not have effect on the step generator offset.
        """
        stepgen_step_source_and_size = self.stepgen_step_source_and_size
        stepgen_step_size = stepgen_step_source_and_size[1]
        stepgen_step_source = stepgen_step_source_and_size[0]
        max_offset = 5.0 * stepgen_step_size

        if abs(offset) > max_offset:
            offset_units = "V" if "VOLTAGE" in stepgen_step_source else "A"
            raise ValueError(
                f'Setting the step generator offset....\n'
                f'Step Generator Offset cannot be greater than the maximum offset done the actual'
                f' step size.\n'
                f'Actual step size = " {stepgen_step_size} {offset_units}.\n'
                f'Then maximun offset is {max_offset} {offset_units}.\n'
                f'You wanted {offset} {offset_units}\n'
            )

        invert = False
        if offset < 0:
            invert = True

        multiplier = abs(offset) / stepgen_step_size

        self.stepgen_step_size_multiplier = multiplier
        if not invert == self.stepgen_invert:
            self.stepgen_invert = invert

    ################################################################################
    # MISCELLANEOUS COMMANDS AND QUERIES
    # The miscellaneous commands and queries group contains queries for the status
    # of the output connectors, and the measurement code, as well as commands to set
    # the measurement mode and save and recall sets of front-panel settings.
    ################################################################################

    measure_mode = Instrument.control(
        "MEAsure?", "MEAsure %s",
        """Control the measurement mode (string).""",
        validator=strict_discrete_set,
        values=VALID_MEASUREMENT_MODES,
        get_process=lambda r:
        r.replace("MEASURE ", "")
    )

    #########################################################################################
    # WAVEFORM TRANSFER COMMANDS AND QUERIES
    # The Waveform Transfer group allows curve or preamble data (or both) to be stored in,
    # or recalled from, mass storage.
    # There is also a command to set the number of curve data points stored
    # and a related query to determine the length of a previously defined waveform.
    #########################################################################################

    waveform_preamble = Instrument.control(
        "WFMpre?", "WFMpre %s",
        """Control the waveform preamble data for the currently displayed waveform (string).""",
        get_process=lambda r:
        r
    )

    waveform_points = Instrument.control(
        "WFMpre?", "WFMpre NR.PT:%s",
        """Control the length of the waveform curve.""",
        get_process=lambda r:
        r
    )

    def fetch_curve(self, bytes_count):
        """
        Asks the instrument for the curve data for the view curve when in view mode
        or the curve data for the current display when in store mode.
        :param bytes_count: The number of bytes to get (read) from the instrument.
        :return: The binary data read with the next structure
        CURVE CURVID:”INDEX 9”,%NNXXYYXXYY . . . XXYYC
        """
        # Curve data sets are usually much longer than any other kind. Typically a set of curve
        # data will be about 4122 bytes long, with most of the bytes being binary-coded numbers.
        # Thus, most of the string of data is not directly readable, but must be interpreted by
        # the controller. An example might look like this. CURVE CURVID:”INDEX 9”,%NNXXYYXXYY . .
        # . XXYYC This example breaks down as follows. It starts with an ASCII string of 25
        # characters: CURVE CURVID:”INDEX 9”,% This is followed by a series of binary bytes. The
        # first of these is two bytes giving the number of data bytes to follow, plus one (
        # typically 4097): NN Then come the 4096 data bytes. Each of the 1024 data points on the
        # curve is represented by four bytes, 2 for the 10 bits of the X coordinate and 2 for the
        # 10 bits of the Y coordinate: XXYYXXYY . . . XXYY And finally there is one byte which is
        # the checksum for the preceding 4098 data bytes.

        log.info("Asking the instrument for the curve data.")
        self.wait_for(self.query_delay)
        self.write("CURve?")
        self.wait_for(self.query_delay)
        # change the response timeout for long responses
        response = self.read_bytes(bytes_count)
        return response

    def get_curve(self):
        """
        Asks the instrument for the curve data (uses the fetch_curve function) and the necessary
        preamble data (uses the waveform_preamble property) and translate the obtained responses
        into a curve object.
        :return: A Curve object instance containg the information about the curve
        and the curve points.
        """
        # Curve data sets are usually much longer than any other kind. Typically a set of curve
        # data will be about 4122 bytes long, with most of the bytes being binary-coded numbers.
        # Thus, most of the string of data is not directly readable, but must be interpreted by
        # the controller. An example might look like this. CURVE CURVID:”INDEX 9”,%NNXXYYXXYY . .
        # . XXYYC This example breaks down as follows. It starts with an ASCII string of 25
        # characters: CURVE CURVID:”INDEX 9”,% This is followed by a series of binary bytes. The
        # first of these is two bytes giving the number of data bytes to follow, plus one (
        # typically 4097): NN Then come the 4096 data bytes. Each of the 1024 data points on the
        # curve is represented by four bytes, 2 for the 10 bits of the X coordinate and 2 for the
        # 10 bits of the Y coordinate: XXYYXXYY . . . XXYY And finally there is one byte which is
        # the checksum for the preceding 4098 data bytes.

        # The first XXYY of the 1024 points is the first point taken whe we execute the sweep.
        # Last point should be the coordinates 0,0.
        # XXYY is coordinate point. Thus, we have to translate it for getting electrical values.

        # Format of the curve data ASCII HEAD (25b) + NN (2b) + XXYYXXYY......XXYY (points to
        # read 1024 points typ) + C (checksum 1b) + EOL

        waveform_preamble = Tektronix371A.WaveformPreamble(self.waveform_preamble)

        curve_head_len = 25  # bytes (ASCII HEAD)
        bytes_for_data_len = 2  # bytes (NN)
        bytes_for_checksum = 1  # bytes
        bytes_per_x_coordinate_point = 2  # bytes
        bytes_per_y_coordinate_point = 2  # bytes
        points_to_read = \
            waveform_preamble.n_measures_readed * \
            (bytes_per_y_coordinate_point + bytes_per_x_coordinate_point)

        raw_data = self.fetch_curve(curve_head_len +
                                    bytes_for_data_len +
                                    points_to_read +
                                    bytes_for_checksum)

        curve = Tektronix371A.Curve(
            waveform_preamble,
            curve_head_len,
            bytes_for_data_len,
            bytes_for_checksum,
            bytes_per_x_coordinate_point,
            bytes_per_y_coordinate_point,
            raw_data
        )

        return curve

    #####################################################################################
    # # STATUS AND EVENT COMMANDS AND QUERIES
    # # The Status and Event Reporting group sets and reports the status of service
    # # requests and operation complete service requests. A query is also included for
    # # the event code of the latest event.
    #####################################################################################

    most_recent_event_code = Instrument.measurement(
        "EVEnt?",
        """Measure the instrument event code of the most recent event""",
        get_process=lambda r:
        Tektronix371A.Tek371AEvent(int(r.replace("EVENT ", "")))
    )

    status_byte = Instrument.measurement(
        "*STB?",
        "Measure the instrument status byte"
    )

    opc = Instrument.control(
        "OPC?", "OPC %s",
        """Control instrument for the status of the operation complete service request (OPC).""",
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True,
        get_process=lambda r:
        r.replace("OPC ", "")
    )

    srq = Instrument.control(
        "RQS?", "RQS %s",
        """Control instrument for the assertion of service reuqests (RQSs).""",
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True,
        get_process=lambda r:
        r.replace("RQS ", "")
    )

    def wait_for_srq(self):
        """
        Suspend execution of the calling thread until srq signal is received from the instrument.
        :return: None
        """
        while not self.srq_called:
            time.sleep(0.1)
        self.srq_called = False

    def discard_and_disable_all_events(self):
        """
        Discard all events (empty the all events in queue) and disable the notification for
        all events via all mechanism.
        :return: None
        """
        self.adapter.connection.discard_events(pyvisa_constants.VI_ALL_ENABLED_EVENTS,
                                               pyvisa_constants.EventMechanism.all)
        self.adapter.connection.disable_event(
            pyvisa_constants.VI_ALL_ENABLED_EVENTS,
            pyvisa_constants.EventMechanism.all)

    def enable_srq_event(self):
        """
        Config the instrument for srq assertion on operation complete
        and creates a function for handling the srq event.
        :return: None
        """

        def event_handler(resource, event, user_handle):
            log.info("Handled event %s on %s", event.event_type, resource)
            log.info("User_Handle %s", user_handle)
            self.srq_called = True

        event_type = pyvisa_constants.VI_EVENT_SERVICE_REQ
        event_mech = pyvisa_constants.EventMechanism.handler
        wrapped = self.adapter.connection.wrap_handler(event_handler)
        self.adapter.connection.install_handler(event_type, wrapped, None)
        self.adapter.connection.enable_event(event_type, event_mech, None)
        self.srq = True
        self.opc = True

    def initialize(self):
        """ Initialize the instrument. Settings are the same as at power-up"""
        log.info("Initializing the instrument.")
        self.write("INIt")
        self.discard_and_disable_all_events()
        time.sleep(1)

    #########################################################################
    #  AUXILIARY CLASSES
    #########################################################################

    class Tek371AEvent(IntFlag):
        """
        Auxiliary class create for translating the instrument 8 bits_status_string into
        an Enum_IntFlag that will help to the user to understand such status.
        """
        # Event code from the instrument has to be interpreted as follows:
        #
        # response --> 'EVENT code'

        #  SYSTEM EVENT CODES
        NO_ERROR = 0
        POWER_ON = 401
        MEASURE_SIGNAL_OPERATION_COMPLETE = 402
        USER_REQUEST = 403

        #  COMMAND ERROR CODES
        COMMAND_HEADER_ERROR = 101
        COMMAND_ARGUMENT_COUNT_ERROR = 102
        COMMAND_ARGUMENT_ERROR = 103
        COMMAND_SYNTAX_ERROR = 106
        WAVEFORM_CHECKSUM_ERROR = 108
        BYTE_COUNT_ERROR = 109

        #  EXECUTION_ERROR CODES
        COMMAND_NOT_EXECUTABLE_IN_LOCAL_MODE = 201
        BUFFER_OVERFLOW = 203
        SETTING_CONFLICTS = 204
        ARGUMENT_OUT_OF_RANGE = 205
        COLLECTOR_SUPPLY_BREAKER_UNMATCH = 272
        NR_PT_AND_BYTE_COUNT_UNMATCH = 273
        NO_WAVEFORM_AVAILABLE = 274
        STEPGEN_SETTING_IN_STEP_GEN_DISABLED_MODE = 275
        FORMAT_ERROR = 276
        NVM_DATA_EMPTY = 277
        NVM_RED_WRITE_ERROR = 278
        CHEKSUM_ERROR = 279
        FD_DATA_EMPTY = 280
        FD_NOT_READY = 281
        WRITE_PROTECT = 282
        DISK_FULL = 283
        INVALID_DATA = 284
        FD_FAULT = 285
        FD_READ_ERROR = 286
        FD_WRITE_ERROR = 287
        FD_SEEK_ERROR = 288

        #  INTERNAL ERROR CODES
        PHASE_LOCK_SYSTEM_FAILED = 353
        COLLECTOR_SUPPLY_OVERHEATED = 354
        COLLECTOR_SUPPLY_FUSE_BLOW = 357
        OUTPUTS_PROTECTED = 350
        INTERLOCK_SYSTEM_FAILED = 358

        #  DEVICE-DEPENDENT EVENT CODES
        SINGLE_MEASUREMENT_COMPLETE = 750
        SWEEP_MEASUREMENT_COMPLETE = 751
        PRINTER_OUTPUT_COMPLETE = 752
        COLLECTOR_SUPPLY_RECOVERED = 753
        COLLECTOR_SUPPLY_BREAKER_CHANGED = 754
        INTERLOCK_SYSTEM_CHANGED = 755
        FORMAT_COMPLETE = 756
        COPY_COMPLETE = 757
        NVM_ERASE_COMPLETE = 758

    class WaveformPreamble:
        """ Represents the waveform preamble for a curve data from the Tektronix model 371A.
        The preamble contains the information needed for interpreting, scaling,
        and labeling the numeric information of the curve.
        This preamble is coded in ASCII characters and is readable by the operator
        without interpretation by the controller.
        """

        # The preamble and curve are each a string of eight-bit bytes.
        # The preamble is a string of ASCII letters, numerals, and punctuation.
        # Each character is represented by one byte.

        # Preambles are necessary to interpret the numeric information in the curve data that
        # follows them. Within a preamble, 26 parameters are specified.
        # The first ten are unique to the 371B curve tracer and are included as a sub-string linked
        # to the WFID: label. The other 16 parameters include ten that have fixed values and
        # six that vary with the particular data sent.
        # Within the WFID: sub-string the parameters are separated by slashes, while the entire
        # sub-string is delimited by a pair of double quote marks.
        # Most of the WFID: string is rather strictly defined,
        # with each parameter value being right justified in a fixed length field.
        # An exception is the BGM value, which may vary in field length. The remainder of the
        # preamble uses standard punctuation. A colon links each parameter label with its
        # corresponding value and the individual label and value pairs are separated with commas.

        # A complete preamble might look like this: WFMPRE WFID:”INDEX 3/VERT 500MA/ HORIZ 1V/STEP
        # 5V/OFFSET 0.00V/BGM 100mS/VCS 12.3/TEXT /HSNS VCE”, ENCDG:BIN, NR.PT:3,PT.FMT:XY,
        # XMULT:+1.0E–2,XZERO:0,XOFF: 12,XUNIT:V,YMULT:+5.0E–3,YZERO:0,YOFF:12, YUNIT:A,BYT/ NR:2,
        # BN.FMT:RP,BIT/NR:10,CRVCHK:CHKSMO,LN.FMT:DOT

        def __init__(self, preamble_array):

            wf_id = preamble_array[0].split("/")
            self.n_measures_readed = int(preamble_array[2].split(":")[1].replace(" ", ""))
            self.x_scale_factor = float(preamble_array[4].split(":")[1].replace(" ", ""))
            self.y_scale_factor = float(preamble_array[8].split(":")[1].replace(" ", ""))
            # screen points, like horizontal pixels in a tv screen
            self.n_horizontal_resolution_points = pow(2, Tektronix371A.ADC_NBITS)
            self.n_vertical_resolution_points = self.n_horizontal_resolution_points
            self.horizontal_range = self.x_scale_factor * self.n_horizontal_resolution_points
            self.vertical_range = self.y_scale_factor * self.n_vertical_resolution_points
            self.horizontal_offset = int(preamble_array[6].split(":")[1].replace(" ", ""))
            self.vertical_offset = int(preamble_array[10].split(":")[1].replace(" ", ""))
            self.horizontal_units = str(preamble_array[7].split(":")[1].replace(" ", ""))
            self.vertical_units = str(preamble_array[11].split(":")[1].replace(" ", ""))

            self.step_size = wf_id[3].removeprefix("STEP").lstrip(" ")
            if 'mV' in self.step_size:
                self.step_size = float(self.step_size.removesuffix("mV")) * 1E-3
            elif 'V' in self.step_size:
                self.step_size = float(self.step_size.removesuffix("V"))

            self.step_offset = wf_id[4].removeprefix("OFFSET").lstrip(" ")
            if 'mV' in self.step_offset:
                self.step_offset = float(self.step_offset.removesuffix("mV")) * 1E-3
            elif 'V' in self.step_offset:
                self.step_offset = float(self.step_offset.removesuffix("V"))

        def __str__(self):

            description = f'The Waveform Preamble is: \n' \
                          f'Number of Measures Readed from: ' \
                          f'{self.n_measures_readed} \n' \
                          f'Horizontal X Scale Factor: ' \
                          f'{self.x_scale_factor} {self.horizontal_units} \n' \
                          f'Number Horizontal Range: ' \
                          f'{self.horizontal_range} \n' \
                          f'Number Horizontal Resolution Points: ' \
                          f'{self.n_horizontal_resolution_points}\n' \
                          f'Horizontal Offset: ' \
                          f'{self.horizontal_offset} \n' \
                          f'Horizontal Units: ' \
                          f'{self.horizontal_units} \n' \
                          f'Vertical Y Scale Factor: ' \
                          f'{self.y_scale_factor} {self.vertical_units} \n' \
                          f'Number Vertical Range: ' \
                          f'{self.vertical_range} \n' \
                          f'Number Vertical Resolution Points: ' \
                          f'{self.n_vertical_resolution_points} \n' \
                          f'Vertical Offset: ' \
                          f'{self.vertical_offset} \n' \
                          f'Vertical Units: ' \
                          f'{self.vertical_units} \n' \
                          f'Step Size: ' \
                          f'{self.step_size} \n' \
                          f'Step Offset: ' \
                          f'{self.step_offset} \n\n'

            return description

    class Curve:
        """ Represents the Tektronix Curve Data from the Tektronix model 371A
        and provides a high-level interface for interacting with and translate
        data to electrical magnitudes.
        """

        # Curve data sets are usually much longer than any other kind.

        # The major part of a curve is a sequence of binary coded numbers,
        # which is prefixed by a 25 character ASCII string identifying the curve.

        # Typically a set of curve data will be about 4122 bytes long, with most of the bytes being
        # binary-coded numbers. Thus, most of the string of data is not directly readable, but must
        # be interpreted by the controller. An example might look like this. CURVE CURVID:”INDEX 9”,
        # %NNXXYYXXYY . . . XXYYC This example breaks down as follows.
        # It starts with an ASCII string of 25 characters: CURVE CURVID:”INDEX 9”,%
        # This is followed by a series of binary bytes.
        # The first of these is two bytes giving the number of data bytes to follow, plus one (
        # typically 4097): NN Then come the 4096 data bytes. Each of the 1024 data points on the
        # curve is represented by four bytes, 2 for the 10 bits of the X coordinate and 2 for the 10
        # bits of the Y coordinate: XXYYXXYY . . . XXYY And finally there is one byte which is the
        # checksum for the preceding 4098 data bytes.

        # The first XXYY of the 1024 points is the first point taken whe we execute the sweep.
        # Last point should be the coordinates 0,0.
        # XXYY is coordinate point. Thus, we have to translate it for getting electrical values.

        def __init__(self,
                     waveform_preamble,
                     n_bytes_for_head,
                     n_bytes_for_data,
                     n_bytes_for_checksum,
                     n_bytes_for_x_coordinate,
                     n_bytes_for_y_coordinate,
                     raw_curve_data):
            """

            :param waveform_preamble: Preambles are necessary to interpret the numeric information
            in the curve data that follows them.
            Within a preamble, 26 parameters are specified.
            The first ten are unique to the 371A curve tracer and are included
            as a sub-string linked to the WFID: label.
            The other 16 parameters include ten that have fixed values and six that vary
            with the particular data sent.
            Within the WFID: sub-string the parameters are separated by slashes,
            while the entire sub-string is delimited by a pair of double quote marks.
            Most of the WFID: string is rather strictly defined, with each parameter value
            being right justified in a fixed length field.
            An exception is the BGM value, which may vary in field length.
            The remainder of the preamble uses standard punctuation.
            A colon links each parameter label with its corresponding value and the individual label
            and value pairs are separated with commas.
            A complete preamble might look like this:
            WFMPRE WFID:”INDEX 3/VERT 500MA/ HORIZ 1V/STEP 5V/OFFSET 0.00V/BGM 100mS/
            VCS 12.3/TEXT /HSNS VCE”,
            ENCDG:BIN, NR.PT:3,PT.FMT:XY,XMULT:+1.0E–2,XZERO:0,XOFF: 12,XUNIT:V,YMULT:+5.0E–3,
            YZERO:0,YOFF:12,YUNIT:A,BYT/ NR:2,BN.FMT:RP,BIT/NR:10,CRVCHK:CHKSMO,LN.FMT:DOT
            :param n_bytes_for_head: The length (number of bytes) the ASCII header information
            needs.
            Typically 25 bytes.
            :param n_bytes_for_data: The length (number of bytes) the number of data bytes
            information needs.
            Typically 2 bytes are needed to indicate the length of the data that follow
            (normally 4096).
            :param n_bytes_for_checksum: The length (number of bytes) the checksum information
            needs.
            Typically 1 bytes is needed to indicate the length of the data of the checksum.
            :param n_bytes_for_x_coordinate: The length (number of bytes) a x coordinate point needs
            to be represented. Typically 2 bytes.
            :param n_bytes_for_y_coordinate: The length (number of bytes) a y coordinate point needs
            to be represented. Typically 2 bytes.
            :param raw_curve_data: The complete curve data set  where an example might look
            like this:
            CURVE CURVID:”INDEX 9”,%NNXXYYXXYY . . . XXYYC where:
            Header = CURVE CURVID:”INDEX 6”,%
            NN = NUmber of data (number of bytes) that follow the header.
            XXYYXXYY . . . XXYY = The data of the curve itself (Every XX or YY are 2 bytes).
            C = The byte for the checksum.
            :type waveform_preamble: WaveformPreamble
            :type n_bytes_for_head: int
            :type n_bytes_for_data: int
            :type n_bytes_for_checksum: int
            :type n_bytes_for_x_coordinate: int
            :type n_bytes_for_y_coordinate: int
            :type raw_curve_data: bytes.
            """

            self.waveform_preamble = waveform_preamble
            self.n_bytes_for_head = n_bytes_for_head
            self.n_bytes_for_data = n_bytes_for_data
            self.raw_curve_data = raw_curve_data
            self.n_bytes_for_checksum = n_bytes_for_checksum
            self.n_bytes_for_x_coordinate = n_bytes_for_x_coordinate
            self.n_bytes_for_y_coordinate = n_bytes_for_y_coordinate

            self.start_points_coordinates_index = self.n_bytes_for_head + self.n_bytes_for_data
            self.stop_points_coordinates_index = len(
                self.raw_curve_data) - self.n_bytes_for_checksum
            self.raw_points_coordinates = self.raw_curve_data[
                                          self.start_points_coordinates_index:
                                          self.stop_points_coordinates_index]

            self.points_coordinates = []  # list of tuples --> (coord_x, coord_y)
            self.points = []  # list of tuples --> (x, y)

            for i in range(len(self.raw_points_coordinates)):

                if (i % 4 == 0) and \
                        (i <= (len(self.raw_points_coordinates) - (
                                self.n_bytes_for_x_coordinate + self.n_bytes_for_y_coordinate))):
                    coord_x = int.from_bytes(
                        self.raw_points_coordinates[i:i + self.n_bytes_for_x_coordinate],
                        byteorder="big",
                        signed=False
                    ) - waveform_preamble.horizontal_offset

                    coord_x = max(coord_x, 0)

                    coord_y = int.from_bytes(self.raw_points_coordinates
                                             [i + self.n_bytes_for_x_coordinate:
                                              i + self.n_bytes_for_x_coordinate +
                                              self.n_bytes_for_y_coordinate],
                                             byteorder="big",
                                             signed=False
                                             ) - waveform_preamble.vertical_offset
                    coord_y = max(coord_y, 0)

                    self.points_coordinates.append((coord_x, coord_y))
                    self.points.append((coord_x * waveform_preamble.x_scale_factor,
                                        coord_y * self.waveform_preamble.y_scale_factor))

        def __str__(self):

            description = f'WAVEFORM DATA \n' \
                          f'{self.waveform_preamble}' \
                          f'The Waveform Curve Data is:\n' \
                          f'Curve Coordinate Points: {self.points_coordinates} \n' \
                          f'Curve Points: {self.points} \n\n'

            return description
