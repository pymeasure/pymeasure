#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

import struct

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import truncated_discrete_set, truncated_range


class VoltageChannel(Channel):
    """
    ===========================================================
    Implementation of a SIGLENT SDS1072CML Oscilloscope channel
    ===========================================================
    """

    vertical_division = Channel.control(
        "C{ch}:VDIV?",
        "C{ch}:VDIV %.2eV",
        "Control the vertical sensitivity of a channel in V/divisions.",
        validator=truncated_range,
        values=[2e-3, 10],
        get_process=lambda v: float(v.split(" ", 1)[-1][:-1]),
    )

    coupling = Channel.control(
        "C{ch}:CPL?",
        "C{ch}:CPL %s1M",
        "Control the channel coupling mode.(DC or AC)",
        validator=truncated_discrete_set,
        values={"DC": "D", "AC": "A"},
        map_values=True,
        get_process=lambda v: v.split(" ", 1)[-1][0],
    )

    def get_waveform(self):
        """Get the waveforms displayed in the channel as a tuple with elements:
        - time: (1d array) the time in seconds since the trigger epoch for every voltage value in
        the waveforms
        - voltages: (1d array) the waveform in V

        """
        self.write("C{ch}:WF? ALL")
        response = self.read_bytes(count=-1, break_on_termchar=True)
        descriptor_dictionary = self.get_descriptor()
        data_points = descriptor_dictionary["numDataPoints"] if descriptor_dictionary["numDataPoints"] else descriptor_dictionary["pointsScreen"]  # noqa: E501
        rawWaveform = list(
            struct.unpack_from(
                "%db" % data_points,
                response,
                offset=descriptor_dictionary["descriptorOffset"],
            ),
        )

        waveform = [
            point * descriptor_dictionary["verticalGain"] - descriptor_dictionary["verticalOffset"]
            for point in rawWaveform
        ]
        timetags = [
            i * descriptor_dictionary["horizInterval"] + descriptor_dictionary["horizOffset"]
            for i in range(len(rawWaveform))
        ]
        return timetags, waveform

    def get_descriptor(self, descriptor=None):
        """Get the descriptor of data being sent when querying device for waveform
        Will decode a descriptor if provided one (Raw byte stream), otherwise it will query it
        :return:
        dict: A dictionary with the keys:
        - numDataPoints: the number of points in the waveform
        - verticalGain: the voltage increment per code value (in V)
        - verticalOffset: the voltage offset to add to the decoded voltage values
        - horizInterval: the time interval between points in s
        - horizOffset:the offset to add to the time steps
        - descriptorOffset: Length of the C1:WF ALL,#9000000346 message

        """
        if descriptor is None:
            command = "C{ch}:WF? DESC"
            self.write(command)
            descriptor = self.read_bytes(count=-1, break_on_termchar=True)
        command = "WFSU?"
        self.write(command)
        wfsu = self.read()
        sparsing = int(wfsu.split(",")[1])
        number = int(wfsu.split(",")[3])
        first = int(wfsu.split(",")[5])
        descriptorOffset = 21
        descriptor_dictionary = {"sparsing": sparsing, "numDataPoints": number, "firstPoint": first}
        variables = [
            ("commType", 32, "h"),
            ("commOrder", 34, "h"),
            ("waveDescLen", 36, "l"),
            # ('numDataPoints',60,'l'),#This seems to give non-sense. A bug in the firmware?
            ("pointsScreen", 120, "l"),
            # ('firstPoint',124,'L'), #same
            ("sparsingFactor", 136, "l"),
            ("numSweeps", 148, "l"),
            ("verticalGain", 156, "f"),
            ("verticalOffset", 160, "f"),
            ("horizInterval", 176, "f"),
            ("horizOffset", 180, "d"),
            ("acqDuration", 312, "f"),
            ("recordType", 316, "h"),
            ("processing", 318, "h"),
            ("timebase", 324, "h"),
            ("vertCoupling", 326, "h"),
            ("probeAtt", 328, "f"),
            ("fixedVertGain", 332, "h"),
            ("bwLim", 334, "h"),
        ]
        for name, offset, format in variables:
            (value,) = struct.unpack_from(
                format,
                descriptor,
                offset=descriptorOffset + offset,
            )
            descriptor_dictionary.update({name: value})
        if descriptor is None:
            descriptor_dictionary.update({"descriptorOffset": descriptorOffset})
        else:
            descriptor_dictionary.update({"descriptorOffset": descriptorOffset + 346})

        return descriptor_dictionary


class TriggerChannel(Channel):
    """
    =========================================
    Implementation of trigger control channel
    =========================================
    """

    trigger_config_dict = {}

    def get_trigger_config(self):
        """Get the current trigger configuration as a dict with keys:
        - "type": condition that will trigger the acquisition of waveforms [EDGE,
        slew,GLIT,intv,runt,drop]
        - "source": trigger source (str, {EX,EX/5,C1,C2})
        - "hold_type": hold type (refer to page 131 of programing guide)
        - "hold_value1": hold value1 (refer to page 131 of programing guide)
        - "level": Level at which the trigger will be set (float)
        - "slope": (str,{POS,NEG,WINDOW}) Triggers on rising, falling or Window.
        - "mode": behavior of the trigger following a triggering event
        (str, {NORM, AUTO, SINGLE,STOP})
        - "coupling":  (str,{AC,DC}) Coupling to the trigger channel

        and updates the internal configuration status
        """
        self.trigger_config_dict.update(self.trigger_setup)
        self.trigger_config_dict.update(self.trigger_level)
        self.trigger_config_dict.update(self.trigger_slope)
        self.trigger_config_dict.update(self.trigger_mode)
        self.trigger_config_dict.update(self.trigger_coupling)
        return self.trigger_config_dict

    trigger_setup = Channel.measurement(
        "TRSE?",
        docs="""Get the current trigger setup as a dict with keys:
        - "type": condition that will trigger the acquisition of waveforms [EDGE,
        slew,GLIT,intv,runt,drop]
        - "source": trigger source (str, {EX,EX/5,C1,C2})
        - "hold_type": hold type (refer to page 131 of programing guide)
        - "hold_value1": hold value1 (refer to page 131 of programing guide)

        """,
        preprocess_reply=lambda v: v.split(" ", 1)[1],
        get_process=lambda v: {
            "type": v[0],
            "source": v[2],
            "hold_type": v[4],
            "hold_value1": v[6],
        },
    )

    trigger_level = Channel.measurement(
        "TRLV?",
        docs="""Get the current trigger level as a dict with keys:
        - "source": trigger source whose level will be changed (str, {EX,EX/5,C1,C2})
        - "level": Level at which the trigger will be set (float)

        """,
        get_process=lambda v: {
            "source": v.split(":", 1)[0],
            "level": float(v.split(" ", 1)[-1][:-2]),
        },
    )

    trigger_slope = Channel.measurement(
        "TRSL?",
        docs="""Get the current trigger slope as a dict with keys:
        - "source": trigger source whose level will be changed (str, {EX,EX/5,C1,C2})
        - "slope": (str,{POS,NEG,WINDOW}) Triggers on rising, falling or Window.

        """,
        get_process=lambda v: {
            "source": v.split(":", 1)[0],
            "slope": v.split(" ", 1)[-1],
        },
    )

    trigger_mode = Channel.measurement(
        "TRMD?",
        docs="""Get the current trigger mode as a dict with keys:
        - "mode": behavior of the trigger following a triggering event
        (str, {NORM, AUTO, SINGLE,STOP})

        """,
        get_process=lambda v: {"mode": v.split(" ", 1)[-1]},
    )

    trigger_coupling = Channel.measurement(
        "TRCP?",
        docs="""Get the current trigger coupling as a dict with keys:
        - "source": trigger source whose coupling will be changed (str, {EX,EX/5,C1,C2})
        - "coupling":  (str,{AC,DC}) Coupling to the trigger channel

        """,
        get_process=lambda v: {
            "source": v.split(":", 1)[0],
            "coupling": v.split(" ", 1)[-1],
        },
    )

    def set_trigger_config(self, **kwargs):
        """Set the current trigger configuration with keys:
        - "type": condition that will trigger the acquisition of waveforms [EDGE,
        slew,GLIT,intv,runt,drop]
        - "source": trigger source (str, {EX,EX/5,C1,C2})
        - "hold_type": hold type (refer to page 131 of programing guide)
        - "hold_value1": hold value1 (refer to page 131 of programing guide)
        - "level": Level at which the trigger will be set (float)
        - "slope": (str,{POS,NEG,WINDOW}) Triggers on rising, falling or Window.
        - "mode": behavior of the trigger following a triggering event
        (str, {NORM, AUTO, SINGLE,STOP})
        - "coupling":  (str,{AC,DC}) Coupling to the trigger channel

        Returns a flag indicating if all specified entries were correctly set on the oscilloscope
        and updates the interal trigger configuration
        """
        trigger_config_dict = self.get_trigger_config()
        # self.trigger_config_dict=trigger_config_dict
        setProcesses = {
            "setup": lambda dictIn: (
                dictIn.get("type"),
                dictIn.get("hold_type"),
                dictIn.get("hold_value1"),
            ),
            "level": lambda dictIn: "%.2eV" % dictIn.get("level"),
            "coupling": lambda dictIn: dictIn.get("coupling"),
            "slope": lambda dictIn: dictIn.get("slope"),
            "mode": lambda dictIn: dictIn.get("mode"),
        }
        setCommands = {
            "setup": "TRSE %s,SR,{ch},HT,%s,HV,%s",
            "level": "{ch}:TRLV %s",
            "coupling": "{ch}:TRCP %s",
            "slope": "{ch}:TRSL %s",
            "mode": "TRMD %s",
        }
        setValues = {  # For a given change in conf dict,find the relevant command to be called
            "setup": ["source", "type", "hold_type", "hold_value1"],
            "level": ["level"],
            "coupling": ["coupling"],
            "slope": ["slope"],
            "mode": ["mode"],
        }
        if kwargs.get("source") is not None:
            self.id = kwargs["source"]
        changedValues = [key for key in kwargs if trigger_config_dict[key] != kwargs[key]]
        processToChange = [
            key for key in setValues if any([value in changedValues for value in setValues[key]])
        ]
        for changedKey in changedValues:
            trigger_config_dict[changedKey] = kwargs[changedKey]
        for processKey in processToChange:
            self.write(
                setCommands[processKey] % setProcesses[processKey](trigger_config_dict),
            )
        self.trigger_config_dict = self.get_trigger_config()
        statusFlag = self.trigger_config_dict == trigger_config_dict
        return statusFlag


class SDS1072CML(SCPIMixin, Instrument):
    """
    ==============================================
    Represents the SIGLENT SDS1072CML Oscilloscope
    ==============================================
    """

    def __init__(self, adapter, name="Siglent SDS1072CML Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)

    channel_1 = Instrument.ChannelCreator(VoltageChannel, "1")
    channel_2 = Instrument.ChannelCreator(VoltageChannel, "2")
    trigger = Instrument.ChannelCreator(TriggerChannel, "")

    time_division = Instrument.control(
        ":TDIV?",
        ":TDIV %.2eS",
        "Control the time division to the closest possible value, rounding downwards, in seconds.",
        validator=truncated_range,
        values=[5e-9, 50],
        get_process=lambda v: float(v.split(" ", 1)[-1][:-1]),
    )

    status = Instrument.measurement(
        "SAST?",
        "Get the sampling status of the scope (Stop, Ready, Trig'd, Armed)",
        get_process=lambda v: v.split(" ", 1)[-1],
    )

    internal_state = Instrument.measurement(
        "INR?",
        "Get the scope's Internal state change register and clears it.",
        get_process=lambda v: v.split(" ", 1)[-1],
    )

    is_ready = Instrument.measurement(
        "SAST?",
        "Get whether the scope is ready for the next acquisition (bool)",
        get_process=lambda v: v.split(" ", 1)[-1] in ["Stop", "Ready", "Armed"],
    )

    def wait(self, time):
        """Stop the scope from doing anything until it has completed the current acquisition (p.146)

        :param time: time in seconds to wait for
        """
        self.write("WAIT %d" % int(time))

    def arm(self):
        """Change the acquisition mode from 'STOPPED' to 'SINGLE'.
        Returns True if the scope is ready and armed."""
        if self.is_ready:
            self.write("ARM")
            return True
        else:
            return False

    waveform_setup = Instrument.control(
        "WFSU?",
        "WFSU SP,%d,NP,%d,FP,%d",
        docs="""
        Control the amount of data in a waveform to be transmitted to the controller with
        a dict containing the keys:
        - sparsing: The interval between data points (0 and 1 are all points, 4 are
        1 out of 4 points, etc...)
        - number: the maximal number of data points to return. 0 is all points
        - first: the index of the data point from which to begin data transfer (0 is first)

        """,
        get_process=lambda v: {"sparsing": int(v[1]), "number": int(v[3]), "first": int(v[5])},
        set_process=lambda dict_in: (
            dict_in.get("sparsing"),
            dict_in.get("number"),
            dict_in.get("first"),
        ),
    )

    template = Instrument.measurement(
        "TMPL?",
        """Get a copy of the template that describes the various logical entities making up a
        complete waveform.
        In particular, the template describes in full detail the variables contained in the
        descriptor part of a waveform.
        """,
    )
