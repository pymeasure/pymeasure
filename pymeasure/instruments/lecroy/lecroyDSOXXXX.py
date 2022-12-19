"""
Author: Paul Haigh
email: paul.haigh@nubis-communications.com
"""

import logging
import time
import re
import numpy as np
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range, strict_discrete_range

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# class ScopeChannel(Channel):
#     """Implementation of a LeCroy DSOXXXX Oscilloscope channel.

#     Implementation modeled on Channel object of Keysight DSOX1102G instrument."""

#     _BOOLS = {True: "ON", False: "OFF"}

#     bwlimit = Instrument.control("BWL?", "BWL %s", """ Toggles the 20 MHz internal low-pass filter. (strict bool)""", validator=strict_discrete_set, values=_BOOLS, map_values=True)

#     coupling = Instrument.control(
#         "CPL?",
#         "CPL %s",
#         """ A string parameter that determines the coupling ("ac 1M", "dc 1M", "ground").""",
#         validator=strict_discrete_set,
#         values={"ac 1M": "A1M", "dc 1M": "D1M", "ground": "GND"},
#         map_values=True,
#     )

#     display = Instrument.control("TRA?", "TRA %s", """Control the display enabled state. (strict bool)""", validator=strict_discrete_set, values=_BOOLS, map_values=True)

#     invert = Instrument.control("INVS?", "INVS %s", """ Toggles the inversion of the input signal. (strict bool)""", validator=strict_discrete_set, values=_BOOLS, map_values=True)

#     offset = Instrument.control(
#         "OFST?",
#         "OFST %.2EV",
#         """ A float parameter to set value that is represented at center of screen in
#         Volts. The range of legal values varies depending on range and scale. If the specified
#         value is outside of the legal range, the offset value is automatically set to the nearest
#         legal value.
#         """,
#     )

#     skew_factor = Instrument.control(
#         "SKEW?",
#         "SKEW %.2ES",
#         """ Channel-to-channel skew factor for the specified channel. Each analog channel can be
#         adjusted + or -100 ns for a total of 200 ns difference between channels. You can use
#         the oscilloscope's skew control to remove cable-delay errors between channels.
#         """,
#         validator=strict_range,
#         values=[-1e-7, 1e-7],
#         preprocess_reply=lambda v: v.rstrip("S"),
#     )

#     probe_attenuation = Instrument.control(
#         "ATTN?",
#         "ATTN %g",
#         """ A float parameter that specifies the probe attenuation. The probe attenuation
#         may be from 0.1 to 10000.""",
#         validator=strict_discrete_set,
#         values={0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000},
#     )

#     scale = Instrument.control("VDIV?", "VDIV %.2EV", """ A float parameter that specifies the vertical scale (units per division) in Volts.""")

#     unit = Instrument.control(
#         "UNIT?",
#         "UNIT %s",
#         """ Unit of the specified trace. Measurement results, channel sensitivity, and trigger
#         level will reflect the measurement units you select. ("A" for Amperes, "V" for Volts).""",
#         validator=strict_discrete_set,
#         values=["A", "V"],
#     )

#     trigger_coupling = Instrument.control(
#         "TRCP?",
#         "TRCP %s",
#         """ A string parameter that specifies the input coupling for the selected trigger sources.
#         • ac    — AC coupling block DC component in the trigger path, removing dc offset voltage
#                   from the trigger waveform. Use AC coupling to get a stable edge trigger when
#                   your waveform has a large dc offset.
#         • dc    — DC coupling allows dc and ac signals into the trigger path.
#         • lowpass  — HFREJ coupling places a lowpass filter in the trigger path.
#         • highpass — LFREJ coupling places a highpass filter in the trigger path.
#         """,
#         validator=strict_discrete_set,
#         values={"ac": "AC", "dc": "DC", "lowpass": "HFREJ", "highpass": "LFREJ"},
#         map_values=True,
#     )

#     trigger_level = Instrument.control(
#         "TRLV?",
#         "TRLV %.2EV",
#         """ A float parameter that sets the trigger level voltage for the active trigger source.
#             When there are two trigger levels to set, this command is used to set the higher
#             trigger level voltage for the specified source. :attr:`trigger_level2` is used to set
#             the lower trigger level voltage.
#             When setting the trigger level it must be divided by the probe attenuation. This is
#             not documented in the datasheet and it is probably a bug of the scope firmware.
#             An out-of-range value will be adjusted to the closest legal value.
#         """,
#     )

#     trigger_level2 = Instrument.control(
#         "TRLV2?",
#         "TRLV2 %.2EV",
#         """ A float parameter that sets the lower trigger level voltage for the specified source.
#         Higher and lower trigger levels are used with runt/slope triggers.
#         When setting the trigger level it must be divided by the probe attenuation. This is
#         not documented in the datasheet and it is probably a bug of the scope firmware.
#         An out-of-range value will be adjusted to the closest legal value.
#         """,
#     )

#     trigger_slope = Instrument.control(
#         "TRSL?",
#         "TRSL %s",
#         """ A string parameter that sets the trigger slope of the specified trigger source.
#         <trig_slope>:={NEG,POS,WINDOW} for edge trigger.
#         <trig_slope>:={NEG,POS} for other trigger
#         """,
#         validator=strict_discrete_set,
#         values={"negative": "NEG", "positive": "POS", "window": "WINDOW"},
#         map_values=True,
#     )

#     _measurable_parameters = [
#         "PKPK",
#         "MAX",
#         "MIN",
#         "AMPL",
#         "TOP",
#         "BASE",
#         "CMEAN",
#         "MEAN",
#         "RMS",
#         "CRMS",
#         "OVSN",
#         "FPRE",
#         "OVSP",
#         "RPRE",
#         "PER",
#         "FREQ",
#         "PWID",
#         "NWID",
#         "RISE",
#         "FALL",
#         "WID",
#         "DUTY",
#         "NDUTY",
#         "ALL",
#     ]

#     display_parameter = Instrument.setting(
#         "PACU %s",
#         """Set the waveform processing of this channel with the specified algorithm and the result
#         is displayed on the front panel. The command accepts the following parameters:
#         Parameter   Description
#         PKPK        vertical peak-to-peak
#         MAX         maximum vertical value
#         MIN         minimum vertical value
#         AMPL        vertical amplitude
#         TOP         waveform top value
#         BASE        waveform base value
#         CMEAN       average value in the first cycle
#         MEAN        average value
#         RMS         RMS value
#         CRMS        RMS value in the first cycle
#         OVSN        overshoot of a falling edge
#         FPRE        preshoot of a falling edge
#         OVSP        overshoot of a rising edge
#         RPRE        preshoot of a rising edge
#         PER         period
#         FREQ        frequency
#         PWID        positive pulse width
#         NWID        negative pulse width
#         RISE        rise-time
#         FALL        fall-time
#         WID         Burst width
#         DUTY        positive duty cycle
#         NDUTY       negative duty cycle
#         ALL         All measurement """,
#         validator=strict_discrete_set,
#         values=_measurable_parameters,
#     )

#     def measure_parameter(self, parameter: str):
#         """Process a waveform with the selected algorithm and returns the specified measurement.
#         :param parameter: same as the display_parameter property
#         """
#         parameter = strict_discrete_set(value=parameter, values=self._measurable_parameters)
#         output = self.ask("PAVA? %s" % parameter)
#         match = re.match(r"^\s*(?P<parameter>\w+),\s*(?P<value>.*)\s*$", output)
#         if match:
#             if match.group("parameter") != parameter:
#                 raise ValueError(f"Parameter {match.group('parameter')} different from {parameter}")
#             return float(match.group("value"))
#         else:
#             raise ValueError(f"Cannot extract value from output {output}")

#     def insert_id(self, command):
#         # only in case of the BWL and PACU commands the syntax is different. Why? SIGLENT Why?
#         if command[0:4] == "BWL ":
#             return "BWL C%d,%s" % (self.id, command[4:])
#         elif command[0:5] == "PACU ":
#             return "PACU %s,C%d" % (command[5:], self.id)
#         else:
#             return "C%d:%s" % (self.id, command)

#     # noinspection PyIncorrectDocstring
#     def setup(self, **kwargs):
#         """Setup channel. Unspecified settings are not modified. Modifying values such as
#         probe attenuation will modify offset, range, etc. Refer to oscilloscope documentation and
#         make multiple consecutive calls to setup() if needed.

#         :param bwlimit: A boolean, which enables 20 MHz internal low-pass filter.
#         :param coupling: "AC 1M", "DC 1M", "ground".
#         :param display: A boolean, which enables channel display.
#         :param invert: A boolean, which enables input signal inversion.
#         :param offset: Numerical value represented at center of screen, must be inside
#                        the legal range.
#         :param skew_factor: Channel-tochannel skew factor from -100ns to 100ns.
#         :param probe_attenuation: Probe attenuation values from 0.1 to 1000.
#         :param scale: Units per division.
#         :param unit: Unit of the specified trace: "A" for Amperes, "V" for Volts
#         :param trigger_coupling: input coupling for the selected trigger sources
#         :param trigger_level: trigger level voltage for the active trigger source
#         :param trigger_level2: trigger lower level voltage for the active trigger source (only
#                                SLEW/RUNT trigger)
#         :param trigger_slope: trigger slope of the specified trigger source
#         """

#         for key, value in kwargs.items():
#             setattr(self, key, value)

#     @property
#     def current_configuration(self):
#         """Read channel configuration as a dict containing the following keys:
#         - "channel": channel number (int)
#         - "attenuation": probe attenuation (float)
#         - "bandwidth_limit": bandwidth limiting enabled (bool)
#         - "coupling": "ac 1M", "dc 1M", "ground" coupling (str)
#         - "offset": vertical offset (float)
#         - "skew_factor": channel-tochannel skew factor (float)
#         - "display": currently displayed (bool)
#         - "unit": "A" or "V" units (str)
#         - "volts_div": vertical divisions (float)
#         - "inverted": inverted (bool)
#         - "trigger_coupling": trigger coupling can be "dc" "ac" "highpass" "lowpass" (str)
#         - "trigger_level": trigger level (float)
#         - "trigger_level2": trigger lower level for SLEW or RUNT trigger (float)
#         - "trigger_slope": trigger slope can be "negative" "positive" "window" (str)
#         """

#         ch_setup = {
#             "channel": self.id,
#             "attenuation": self.probe_attenuation,
#             "bandwidth_limit": self.bwlimit,
#             "coupling": self.coupling,
#             "offset": self.offset,
#             "skew_factor": self.skew_factor,
#             "display": self.display,
#             "unit": self.unit,
#             "volts_div": self.scale,
#             "inverted": self.invert,
#             "trigger_coupling": self.trigger_coupling,
#             "trigger_level": self.trigger_level,
#             "trigger_level2": self.trigger_level2,
#             "trigger_slope": self.trigger_slope,
#         }
#         return ch_setup


class LeCroyDSOXXXX(Instrument):

    # _BOOLS = {True: "ON", False: "OFF"}

    # WRITE_INTERVAL_S = 0.02  # seconds

    # channels = Instrument.ChannelCreator(ScopeChannel, (1, 2, 3, 4))

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, name="LeCroy DSOXXXX Oscilloscope", includeSCPI=True, **kwargs)
        # if self.adapter.connection is not None:
        #     self.adapter.connection.timeout = 3000
        # self._grid_number = 10  # Number of grids in the horizontal direction
        # self._seconds_since_last_write = 0  # Timestamp of the last command
        # self._header_size = 16  # bytes
        # self._footer_size = 2  # bytes
        # self.waveform_source = "C1"
        self.default_setup()

    ################
    # System Setup #
    ################

    def default_setup(self):
        """Set up the oscilloscope for remote operation.

        The COMM_HEADER command controls the
        way the oscilloscope formats response to queries. This command does not affect the
        interpretation of messages sent to the oscilloscope. Headers can be sent in their long or
        short form regardless of the CHDR setting.
        By setting the COMM_HEADER to OFF, the instrument is going to reply with minimal
        information, and this makes the response message much easier to parse.
        The user should not be fiddling with the COMM_HEADER during operation, because
        if the communication header is anything other than OFF, the whole driver breaks down.
        """
        self._comm_header = "OFF"
