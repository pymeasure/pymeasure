#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
import time
from enum import IntFlag

import numpy as np

from pymeasure.instruments import Instrument, SCPIMixin, cast_or_str
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


#: Numbers of samples per trace, in the order the ``STATUS:RESOLUTION`` command indexes them.
RESOLUTIONS = (200, 500, 1000, 1500, 2000)

#: Resolution names, in the same order; the software accepts them instead of the index.
RESOLUTION_NAMES = ("very low", "low", "medium", "high", "very high")

#: Numbers of averaged measurements, in the order the ``STATUS:AVERAGE`` command indexes them.
AVERAGES = (1, 2, 4, 8, 16)


def parse_resolution(reply):
    """Convert a ``STATUS:RESOLUTION?`` reply into a number of samples per trace.

    The software answers with the number of samples, while the manual documents the index,
    the number of samples and a name as equivalent notations, so all three are accepted here.

    :param reply: the reply of the instrument (str).
    :returns: number of samples per trace (int).
    :raises ValueError: if the reply is none of the three notations.
    """
    reply = reply.strip().lower()
    if reply in RESOLUTION_NAMES:
        return RESOLUTIONS[RESOLUTION_NAMES.index(reply)]
    value = int(reply)
    if value in RESOLUTIONS:
        return value
    if 0 <= value < len(RESOLUTIONS):
        return RESOLUTIONS[value]
    raise ValueError(f"Cannot interpret '{reply}' as a resolution.")


def parse_averages(reply):
    """Convert a ``STATUS:AVERAGE?`` reply into a number of averaged measurements.

    The software answers with a name followed by the number in brackets, e.g. ``'Off'`` or
    ``'Low (2)'``, while the manual documents the index the set command expects. A bare number
    is read as the number of measurements where that is possible, and as the index otherwise,
    so the indices 1, 2 and 4 cannot be told apart from the counts of the same name.

    :param reply: the reply of the instrument (str).
    :returns: number of measurements averaged into one trace (int).
    :raises ValueError: if the reply is neither a name nor a count nor an index.
    """
    reply = reply.strip().lower()
    if "(" in reply:
        return int(reply[reply.index("(") + 1:reply.index(")")])
    if reply.startswith("off"):
        return 1
    value = int(reply)
    if value in AVERAGES:
        return value
    if 0 <= value < len(AVERAGES):
        return AVERAGES[value]
    raise ValueError(f"Cannot interpret '{reply}' as a number of averages.")


class OperationStatus(IntFlag):
    """Represent the operation status of the software, as returned by ``*OPER?``."""

    DISCONNECTED = 1 << 0
    VISA_CONNECTED = 1 << 1
    DEVICE_INITIALIZED = 1 << 2
    DEVICE_READY = 1 << 3
    DEVICE_BUSY = 1 << 4
    STANDBY = 1 << 5  #: delay motor switched off
    DATA_ERROR = 1 << 6  #: ACF not valid, see :attr:`PulseCheckUSB.data_errors`
    SOFTWARE_ERROR = 1 << 7
    FIRMWARE_ERROR = 1 << 8  #: see :attr:`PulseCheckUSB.firmware_errors`
    SHUTDOWN = 1 << 9
    SERVICE_MODE = 1 << 10


class InitializationStatus(IntFlag):
    """Represent the initialization status of the device, as returned by ``*INIT?``."""

    LINK_OK = 1 << 2
    OPTIC_OK = 1 << 3


class BusyStatus(IntFlag):
    """Represent the busy status of the device, as returned by ``*BUSY?``."""

    IDLE = 1 << 0
    NEW_DATA = 1 << 1
    MEASUREMENT_RUNNING = 1 << 2
    FIT_RUNNING = 1 << 3


class DataError(IntFlag):
    """Represent quality problems of the measured autocorrelation, as returned by ``*ERR?``."""

    SIGNAL_TOO_LOW = 1 << 0
    SIGNAL_TOO_HIGH = 1 << 1
    NO_PEAK_FOUND = 1 << 2
    ASYMMETRIC_ACF = 1 << 3
    DYNAMIC_RANGE_TOO_LOW = 1 << 4
    SCAN_RANGE_TOO_LOW = 1 << 5
    NEGATIVE_OFFSET = 1 << 6


class FirmwareError(IntFlag):
    """Represent the firmware errors of the controller, as returned by ``*FRMW?``."""

    PARSER_ERROR = 1 << 0
    PARAMETER_ERROR = 1 << 1
    FRAM_ERROR = 1 << 2
    # the manual names both bit 3 and bit 4 "I2C-0 Error"
    I2C_0_ERROR = 1 << 3
    I2C_1_ERROR = 1 << 4
    I2C_LOCKED = 1 << 5
    CONFIGURATION_ERROR = 1 << 6
    OPTICS_ERROR = 1 << 7
    BUFFER_OVERFLOW = 1 << 8
    DMA_ERROR = 1 << 9
    USB_ERROR = 1 << 10
    DATA_TIMEOUT = 1 << 11


class PulseCheckUSB(SCPIMixin, Instrument):
    """Represent the APE pulseCheck USB autocorrelator.

    The autocorrelator is attached via USB to a Windows PC running the APE pulseLink control
    software, and that software provides the remote interface: it has to be running, and its
    TCP/IP port has to be enabled under ``Extras`` → ``TCP`` (APE recommends a port number
    between 50000 and 64000). This driver connects to that port, either on the local machine or
    over the network::

        from pymeasure.instruments.ape import PulseCheckUSB

        pulse_check = PulseCheckUSB("TCPIP::192.168.0.10::51123::SOCKET")
        print(pulse_check.id)
        pulse_check.measurement_running = True
        delay, intensity = pulse_check.acf

    Do not send these commands to the controller over USB directly, and note that the older
    pulseCheck models with an RS232 port use a different command set, see
    :class:`~pymeasure.instruments.ape.pulsecheck.PulseCheck`.

    The software implements only part of the SCPI standard commands, :attr:`options` and
    :attr:`next_error` are not among them. It also applies a new setting asynchronously, so
    reading a property back right after writing it may still yield the previous value; allow
    for about a second, and see :attr:`gain` for the detector settings.

    :param adapter: pyvisa resource name of the PC running the pulseLink software, or an
        adapter instance.
    :param name: name of the instrument.
    :param connection_delay: how long to wait after opening the connection, in s. Only applies
        if this call opened it; wait yourself when handing in a ready-made adapter.
    :param kwargs: any valid key-word argument for :class:`~pymeasure.instruments.Instrument`.
    """

    def __init__(self, adapter, name="APE pulseCheck USB", connection_delay=1, **kwargs):
        kwargs.setdefault("write_termination", "\r\n")
        kwargs.setdefault("read_termination", "\n")
        kwargs.setdefault("timeout", 5000)
        super().__init__(adapter, name, **kwargs)
        if isinstance(adapter, (int, str)):
            # only when this call opened the connection: the software silently drops commands
            # sent right after. A ready-made adapter is assumed to be connected already.
            time.sleep(connection_delay)

    def read(self):
        """Read a reply, discarding the padding null bytes the software may add.

        :raises ValueError: if the software did not understand the command.
        """
        reply = super().read().replace("\x00", "").strip()
        if reply == "Parser error":
            raise ValueError(f"{self.name} did not understand the command.")
        return reply

    def _read_block(self):
        """Read the payload of a definite length block, whose ``#`` is already consumed.

        :returns: the payload of the block (bytes).
        """
        digits = int(self.read_bytes(1))
        return self.read_bytes(int(self.read_bytes(digits)))

    def _read_trace(self, command):
        """Read a trace transferred as a block of interleaved intensity and delay values.

        :param command: query returning the trace.
        :returns: a tuple ``(delay, intensity)`` of numpy arrays, with the delay in s.
        """
        self.write(command)
        start = self.read_bytes(1)
        if start != b"#":
            raise ValueError(f"Expected a data block in reply to '{command}', but got "
                             f"'{start.decode(errors='replace') + self.read()}'.")
        payload = self._read_block()
        if not payload or len(payload) % 16:
            # without valid data the software sends a message instead, e.g. "Time out"
            raise ValueError(f"{self.name} sent '{payload.decode(errors='replace')}' instead of "
                             f"trace data, check whether the measurement is running.")
        # the block holds little-endian doubles as [y0, x0, y1, x1, ...] with x the delay in ps
        values = np.frombuffer(payload, dtype="<f8")
        # `values` is a read-only view of the reply, so copy what is not built anew anyway
        return values[1::2] * 1e-12, values[0::2].copy()

    device_name = Instrument.measurement(
        "SYSTEM:DEVICE?",
        """Get the device name (str).""",
        cast=str,
        maxsplit=0,
    )

    serial_number = Instrument.measurement(
        "SYSTEM:SNUMBER?",
        """Get the serial number of the device (str).""",
        cast=str,
        maxsplit=0,
    )

    software_version = Instrument.measurement(
        "SYSTEM:SOFTWARE?",
        """Get the version of the pulseLink control software (str).""",
        cast=str,
        maxsplit=0,
    )

    hardware_version = Instrument.measurement(
        "SYSTEM:HARDWARE?",
        """Get the hardware version of the device (str).""",
        cast=str,
        maxsplit=0,
    )

    firmware_version = Instrument.measurement(
        "SYSTEM:FIRMWARE?",
        """Get the firmware version of the controller (str).""",
        cast=str,
        maxsplit=0,
    )

    motor_type = Instrument.measurement(
        "SYSTEM:MOTOR?",
        """Get the type of the delay motor (str).""",
        cast=str,
        maxsplit=0,
    )

    operation_status = Instrument.measurement(
        "*OPER?",
        """Get the operation status of the software (:class:`OperationStatus`).""",
        cast=int,
        get_process=OperationStatus,
    )

    initialization_status = Instrument.measurement(
        "*INIT?",
        """Get the initialization status of the device (:class:`InitializationStatus`).""",
        cast=int,
        # the upper four bits are documented as always being "1"
        get_process=lambda value: InitializationStatus(value & 0x0F),
    )

    busy_status = Instrument.measurement(
        "*BUSY?",
        """Get the busy status of the device (:class:`BusyStatus`).""",
        cast=int,
        get_process=BusyStatus,
    )

    data_errors = Instrument.measurement(
        "*ERR?",
        """Get the quality problems of the measured autocorrelation (:class:`DataError`).""",
        cast=int,
        get_process=DataError,
    )

    firmware_errors = Instrument.measurement(
        "*FRMW?",
        """Get the errors reported by the controller firmware (:class:`FirmwareError`).""",
        cast=int,
        get_process=FirmwareError,
    )

    measurement_running = Instrument.control(
        "STATUS:START?", "STATUS:START=%d",
        """Control whether the measurement is running (bool).

        Setting this is equivalent to the "Start" button of the pulseLink software. The manual
        documents the query only, but the set command works as well (pulseLink 1.9.3.12).
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    averages = Instrument.control(
        "STATUS:AVERAGE?", "STATUS:AVERAGE=%d",
        """Control the number of measurements averaged into one trace
        (int, one of 1, 2, 4, 8, 16).""",
        validator=strict_discrete_set,
        values=AVERAGES,
        set_process=AVERAGES.index,
        cast=str,
        get_process=parse_averages,
    )

    resolution = Instrument.control(
        "STATUS:RESOLUTION?", "STATUS:RESOLUTION=%d",
        """Control the number of samples per trace
        (int, one of 200, 500, 1000, 1500, 2000).""",
        validator=strict_discrete_set,
        values=RESOLUTIONS,
        set_process=RESOLUTIONS.index,
        cast=str,
        get_process=parse_resolution,
    )

    fit_type = Instrument.control(
        "STATUS:FITTYPE?", "STATUS:FITTYPE=%d",
        """Control the model fitted to the autocorrelation
        (str, one of 'none', 'gaussian', 'sech2', 'lorentz').""",
        validator=strict_discrete_set,
        values={"none": 0, "gaussian": 1, "sech2": 2, "lorentz": 3},
        map_values=True,
    )

    filter_enabled = Instrument.control(
        "STATUS:FILTER?", "STATUS:FILTER=%d",
        """Control whether the autocorrelation is filtered (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    scan_range = Instrument.control(
        "MOTOR:SCANRANGE?", "MOTOR:SCANRANGE=%d",
        """Control the scan range in s (float, one of 0, 150e-15, 500e-15, 1.5e-12, 5e-12,
        15e-12, 50e-12, 150e-12).

        A scan range of 0 stops the delay drive at the zero position. Which of the ranges are
        available depends on the configuration of the device.
        """,
        validator=strict_discrete_set,
        values={0: 0, 150e-15: 150, 500e-15: 500, 1.5e-12: 1500, 5e-12: 5000,
                15e-12: 15000, 50e-12: 50000, 150e-12: 150000},
        map_values=True,
    )

    gain = Instrument.control(
        "DETECTOR:GAIN?", "DETECTOR:GAIN=%d",
        """Control the detector gain (int strictly from 300 to 1000).

        The software passes the detector settings on to the controller only once a further
        command reaches it, and answers with the previous value until then. Reading in a loop
        does not help, since queries do not trigger the update either; write the value twice
        if the read back has to agree immediately.
        """,
        validator=strict_range,
        values=(300, 1000),
        cast=int,
    )

    autogain_enabled = Instrument.control(
        "DETECTOR:AUTOGAIN?", "DETECTOR:AUTOGAIN=%d",
        """Control whether the gain is adjusted automatically (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    sensitivity = Instrument.control(
        "DETECTOR:SENSITIVITY?", "DETECTOR:SENSITIVITY=%d",
        """Control the detector sensitivity (int, 1 for low or 10 for high sensitivity, 100
        with the optional "HighSen" feature).

        The read back lags behind a change in the same way as the one of :attr:`gain`, and the
        software passes a new sensitivity on only while the measurement is running, taking up
        to several seconds to do so.
        """,
        validator=strict_discrete_set,
        values=(1, 10, 100),
        cast=int,
    )

    trigger_level = Instrument.measurement(
        "TRIGGER:LEVEL?",
        """Get the trigger level in V (float from 0.2 to 5).""",
        get_process=lambda value: value * 1e-3,
    )

    trigger_delay = Instrument.measurement(
        "TRIGGER:DELAY?",
        """Get the trigger delay in s (float from 1e-6 to 50e-6).""",
        get_process=lambda value: value * 1e-6,
    )

    trigger_frequency = Instrument.measurement(
        "TRIGGER:FREQUENCY?",
        """Get the trigger frequency in Hz (float).""",
    )

    trigger_impedance = Instrument.measurement(
        "TRIGGER:IMPEDANCE?",
        """Get the trigger impedance in Ohm (float).""",
    )

    @property
    def acf(self):
        """Get the raw autocorrelation as a tuple ``(delay, intensity)`` of numpy arrays, with
        the delay in s and the intensity in arbitrary units.

        The measurement has to be running for the data to be valid.
        """
        return self._read_trace("ACF:DATA?")

    @property
    def displayed_acf(self):
        """Get the autocorrelation as displayed by the software, i.e. with filtering and
        averaging applied, as a tuple ``(delay, intensity)`` of numpy arrays, with the delay in
        s and the intensity in arbitrary units.
        """
        return self._read_trace("ACF:DISPLAYED_ACF?")

    @property
    def acf_mean_data(self):
        """Get the mean values of the autocorrelation as a dict with the keys 'average',
        'delay_max', 'delay_min' (in s), 'intensity_max' and 'intensity_min'.
        """
        self.write("ACF:MEANDATA?")
        start = self.read_bytes(1)
        # the software sends this reply as a plain line, but falls back to a block holding a
        # message, e.g. "Time out", whenever it has no valid data
        reply = self._read_block().decode(errors="replace") if start == b"#" \
            else start.decode(errors="replace") + self.read()
        # read() cannot spot this itself, since the first character was consumed above
        if reply == "Parser error":
            raise ValueError(f"{self.name} did not understand the command.")
        values = reply.split(";")
        if len(values) != 5:
            raise ValueError(f"{self.name} sent '{reply}' instead of the mean values, check "
                             f"whether the measurement is running.")
        average, delay_max, delay_min, intensity_max, intensity_min = map(float, values)
        return {
            "average": average,
            "delay_max": delay_max * 1e-12,
            "delay_min": delay_min * 1e-12,
            "intensity_max": intensity_max,
            "intensity_min": intensity_min,
        }

    fwhm = Instrument.measurement(
        "ACF:FWHM?",
        """Get the FWHM of the measured autocorrelation in s (float).""",
        cast=cast_or_str(float),
        # float() raises with a helpful message if the software reports a problem instead
        get_process=lambda value: float(value) * 1e-12,
    )

    fit_fwhm = Instrument.measurement(
        "ACF:FITFWHM?",
        """Get the FWHM of the fitted autocorrelation in s (float).

        Use :attr:`fit_type` to select the model that is fitted; without a fit the software
        answers with "No fit data" instead of a value.
        """,
        cast=cast_or_str(float),
        # float() raises with a helpful message if the software has no fit to report
        get_process=lambda value: float(value) * 1e-12,
    )

    fix_shutter_open = Instrument.control(
        "SHUTTER:FIX?", "SHUTTER:FIX=%d",
        """Control whether the shutter of the fixed arm is open (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    scan_shutter_open = Instrument.control(
        "SHUTTER:SCAN?", "SHUTTER:SCAN=%d",
        """Control whether the shutter of the scanning arm is open (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    crystal_position = Instrument.control(
        "XTAL:TUNING?", "XTAL:TUNING=%d",
        """Control the position of the phase matching crystal
        (int strictly from 500 to 11000).""",
        validator=strict_range,
        values=(500, 11000),
        cast=int,
    )

    crystal_wavelength = Instrument.setting(
        "XTAL:LAMBDATUNE=%d",
        """Set the phase matching crystal to the position calibrated for a laser wavelength in
        nm (int).

        The manual documents no limits, since the range that makes sense depends on the optics
        set installed, e.g. 700 to 1100 nm for NIR or 1000 to 1600 nm for IR.

        There is no counterpart to read the wavelength back: ``XTAL:LAMBDATUNE?`` answers with
        the crystal position, just like :attr:`crystal_position`.
        """,
    )

    crystal_moving = Instrument.measurement(
        "XTAL:MOVE?",
        """Get whether the crystal motor is moving (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    crystal_type = Instrument.measurement(
        "XTAL:SETXTAL?",
        """Get the type of the phase matching crystal (str).""",
        cast=str,
        maxsplit=0,
    )

    def check_errors(self):
        """Read the errors the controller firmware reports.

        The software does not implement the SCPI error queue, the firmware error register is
        read instead. Problems with the measured autocorrelation itself are not errors in this
        sense, see :attr:`data_errors` for those.

        :returns: list of the firmware errors, empty if there are none.
        """
        errors = self.firmware_errors
        if not errors:
            return []
        log.error("%s: %s", self.name, errors)
        # test each flag bit with a bitwise AND; iterating `errors` itself would need Python 3.11
        return [error for error in FirmwareError if error & errors]
