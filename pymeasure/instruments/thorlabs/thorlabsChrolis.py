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

import os
import logging
import weakref
import pandas as pd
from ctypes import (cdll, create_string_buffer, c_uint8, c_uint16, c_uint32,
                    c_int16, c_int32, c_char_p, c_wchar_p, c_bool, c_double,
                    byref)
from pymeasure.instruments.thorlabs import ThorlabsDLLInstrument
from pymeasure.instruments.validators import (strict_range,
                                              strict_discrete_set,
                                              strict_discrete_range)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class _ThorlabsChrolisBase():
    """Base class to inherit further supporting
    instrument classes from. Provides interface
    to the insturment adapter via
    :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    method.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    def __init__(self, dll=None):
        if dll is not None:
            self.dll = dll


class ThorlabsChrolis(ThorlabsDLLInstrument):
    """Thorlabs Chrolis LED source.
    Access LED specific properties via e.g. ``.LED365``
    attribute for 365nm LED. Properties are provided by
    :class:`~pymeasure.instruments.thorlabs.thorlabsChrolis.ChrolisLED`.

    Access the timing unit via the ``.TU`` attribute. Methods are
    provided by
    :class:`~pymeasure.instruments.thorlabs.thorlabsChrolis.ChrolisTU`.

    :param adapter: instance of adapter
    :type adapter: :class:`ThorlabsChrolisAdapter`
    :param resourceName: resource name as given by
                        :meth:`ThorlabsChrolisAdapter.get_resource_name`
    :type resourceName: str
    :param name: name for the instrument
    :type name: str
    :param id_query: query ID of instrument, defaults to True
    :type id_query: bool, optional
    :param reset: reset instrument, defaults to False
    :type reset: bool, optional
    """
    def __init__(self, adapter, resourceName, name,
                 id_query=True, reset=False):
        super().__init__(
            adapter, resourceName, name, id_query, reset)
        # add properties for individual LEDs via e.g. .LED365 attribute
        names = self.LED_names
        for index in range(6):
            setattr(
                self, names[index].rstrip(' nm').replace(' ', ''),
                # results e.g. in LED365
                _ChrolisLED(self.dll, index + 1, names[index]))

        # add Timing Unit
        self.TU = _ChrolisTU(self.dll)

    def self_test(self):
        """Run device self test routine."""
        result = c_uint16(0)
        message = create_string_buffer(256)
        self.dll(
            'selfTest', byref(result), byref(message))
        message = message.value.decode('ascii').strip()
        return (result.value, message)

    @property
    def revision(self):
        """Revision numbers of driver and firmwares."""
        instr_drv = create_string_buffer(256)
        chrolis_FW = create_string_buffer(256)
        TU_FW = create_string_buffer(256)
        self.dll(
            'revisionQuery',
            byref(instr_drv), byref(chrolis_FW), byref(TU_FW))
        (instr_drv, chrolis_FW, TU_FW) = tuple(
            x.value.decode('ascii').strip()
            for x in (instr_drv, chrolis_FW, TU_FW))
        return {
            "Instrument Driver Revision": instr_drv,
            "Chrolis Firmware Revision": chrolis_FW,
            "Timing Unit Firmware Revision": TU_FW}

    @property
    def id(self):
        """Return device identification information.

        :return: Manufacturer, Device Name, Serial Number
        :rtype: dict
        """
        deviceName = create_string_buffer(256)
        serialNumber = create_string_buffer(256)
        manufacturerName = create_string_buffer(256)
        self.dll(
            'identificationQuery', byref(manufacturerName),
            byref(deviceName), byref(serialNumber))
        (deviceName, serialNumber, manufacturerName) = tuple(
            x.value.decode('ascii').strip()
            for x in (deviceName, serialNumber, manufacturerName))
        return {
            "Manufacturer": manufacturerName,
            "Device Name": deviceName,
            "Serial Number": serialNumber}

    @property
    def box_status(self):
        """Current status of the device."""
        status = c_uint32(0)
        self.dll('getBoxStatus', byref(status))
        status = "{0:07b}".format(status.value)  # 7bit representation
        status = tuple(bool(x) for x in status)
        status = reversed(status)
        codes = ('Box is open', 'LLG not connected', 'Interlock is open',
                 'Using default adjustment', 'Box overheated',
                 'LED overheated', 'Box setup invalid')
        message = ''
        for i, flag in enumerate(status):
            if flag is False:
                # lower bit indicates status
                message += codes[i] + ', '
        message = message.rstrip(', ')
        return message

    @property
    def box_temperature(self):
        """Temperature of Chrolis in °C."""
        temp = c_double(0)
        self.dll('getBoxTemperature', byref(temp))
        return temp.value

    @property
    def cpu_temperature(self):
        """CPU temperature of Chrolis in °C."""
        temp = c_double(0)
        self.dll('getCPUTemperature', byref(temp))
        return temp.value

    @property
    def llg_temperature(self):
        """Liquid light guide (LLG) temperature in °C."""
        temp = c_double(0)
        self.dll(
            'getLLGTemperature', byref(temp))
        return temp.value

    @property
    def LED_linear_mode(self):
        """Relative brightness of all LEDs in %.
        Resolution: 0.1%
        """
        brightness = c_uint16(0)
        self.dll('getLED_LinearModeValue', byref(brightness))
        return brightness.value/10

    @LED_linear_mode.setter
    def LED_linear_mode(self, brightness):
        brightness = strict_range(brightness*10, (0, 1000))
        self.dll('setLED_LinearModeValue', c_uint16(brightness))

    ########################################
    # LED Settings (commands for all 6 LEDs simultaneously)
    ########################################
    def _read_LED_parameters(self, command, datatype, init_value):
        """Helper method to read parameter of all 6 LEDs.
        """
        values = tuple(datatype(init_value) for i in range(6))
        # datatype(init_value) needs to be executed here to get
        # 6 different memory locations
        # otherwise all values are the same
        self.dll(command, *[byref(v) for v in values])
        return tuple(v.value for v in values)

    def _set_LED_parameters(self, command, values, datatype,
                            validator=lambda v: v):
        """Helper method to set parameters for all 6 LEDs.
        """
        if len(values) != 6:
            raise ValueError(
                'LED parameters are required to have exactly 6 values')
        values = tuple(validator(v) for v in values)
        self.dll(command, *[datatype(v) for v in values])

    @property
    def LED_names(self):
        """Get LED names."""
        ret = self._read_LED_parameters(
            'readLED_HeadsName', create_string_buffer, 256)
        ret = tuple(x.decode('ascii').strip() for x in ret)
        return ret

    @property
    def brightness(self):
        """Set brightness of all 6 LEDs in %.
        Resolution: 0.1%
        """
        ret = self._read_LED_parameters(
            'getLED_HeadBrightness', c_uint16, 0)
        return tuple(x/10 for x in ret)

    @brightness.setter
    def brightness(self, led_brightness):
        led_brightness = tuple(int(x*10) for x in led_brightness)
        log.info(
            '{0}: Set LED Brightnesses (0-1000) to {1}'.format(
                self.name, led_brightness))
        self._set_LED_parameters(
            'setLED_HeadBrightness', led_brightness, c_uint16,
            validator=lambda v: strict_range(v, (0, 1000)))

    @property
    def power_state(self):
        """Set power state of all 6 LEDs."""
        return self._read_LED_parameters(
            'getLED_HeadPowerStates', c_bool, 0)

    @power_state.setter
    def power_state(self, power):
        log.info('{0}: Set LED power states to {1}'.format(
            self.name, power))
        self._set_LED_parameters(
            'setLED_HeadPowerStates', power, c_bool,
            validator=lambda v: strict_discrete_set(v, (True, False, 0, 1)))

    def all_LEDs_off(self):
        """Set power state of all 6 LEDs to off."""
        self.power_state = [False for i in range(6)]

    @property
    def LED_temperature(self):
        """Return temperature of LEDs in °C."""
        return self._read_LED_parameters(
            'getLED_HeadTemperature', c_double, 0)

    @property
    def LED_cathode_voltage(self):
        """Return cathode voltage of LEDs in V."""
        return self._read_LED_parameters(
            'getLED_HeadMeasCathodeVoltage', c_double, 0)

    @property
    def LED_current(self):
        """Return current of LEDs in A."""
        return self._read_LED_parameters(
            'getLED_HeadMeasCurrent', c_double, 0)


########################################
# Individual LED
########################################
class _ChrolisLED(_ThorlabsChrolisBase):
    """Interface to individual LEDs of Throlabs Chrolis.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    :param channel_index: channel index of LED (1-6)
    :type channel_index: int
    :param name: name of LED
    :type name: str
    """
    def __init__(self, dll, channel_index, name):
        super().__init__(dll=dll)
        self.name = name
        channel_index = strict_range(channel_index, (1, 6))
        self.channel = c_uint8(channel_index)

    @property
    def centroid_wavelength(self):
        """Centroid wavelength of LED in nm."""
        wavelength = c_uint16(0)
        self.dll('readLED_HeadCentroidWL', self.channel, byref(wavelength))
        return wavelength.value

    @property
    def peak_wavelength(self):
        """Peak wavelength of LED in nm."""
        wavelength = c_uint16(0)
        self.dll('readLED_HeadPeakWL', self.channel, byref(wavelength))
        return wavelength.value

    @property
    def FWHM_wavelength(self):
        """Full width half max wavelentgh (FWHM) range of the LED in nm.
        """
        lower_wl = c_uint16(0)
        upper_wl = c_uint16(0)
        self.dll(
            'readLED_HeadFWHMW',
            self.channel, byref(lower_wl), byref(upper_wl))
        return (lower_wl.value, upper_wl.value)

    @property
    def Ooe2_wavelength(self):
        """1/e^2 range of the LED in nm."""
        lower_wl = c_uint16(0)
        upper_wl = c_uint16(0)
        self.dll(
            'readLED_HeadOoe2',
            self.channel, byref(lower_wl), byref(upper_wl))
        return (lower_wl.value, upper_wl.value)

    @property
    def wavelength_range(self):
        """Wavelength range of LED in nm.
        """
        min_wl = c_uint16(0)
        max_wl = c_uint16(0)
        self.dll(
            'readLED_HeadSpectrumRange',
            self.channel, byref(min_wl), byref(max_wl))
        return (min_wl.value, max_wl.value)

    @property
    def spectrum(self):
        """Read spectrum of LED (relative power).

        :return: spectrum: power vs. wavelength
        :rtype: Pandas dataframe
        """
        nop = c_uint16(0)
        wavelength = (c_uint16 * 1000)()
        norm_power = (c_double * 1000)()
        self.dll(
            'readLED_HeadSpectrum',
            self.channel, byref(nop), byref(wavelength),
            byref(norm_power))
        return pd.DataFrame({
            'wavelength': wavelength[:nop.value],
            'power': norm_power[:nop.value]
            })


########################################
# Timing Unit
########################################
class _ChrolisTU(_ThorlabsChrolisBase):
    """Timing unit of the Throlabs Chrolis.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """

    def reset(self):
        """This function resets the sequence configuration
        of the timing unit.
        Use this function always at the beginning of
        programming a new sequence configuration.
        """
        self.dll('TU_ResetSequence')

    def add_directly_triggered_signal(self, channel_index):
        """This function programs a signal of the timing unit.
        This output signal will toggle when a trigger condition set
        with command :meth:`add_trigger_point` is met.
        The toggling will start after the sequence is enabled by
        sending command :meth:`start_stop_output`.

        :param channel_index: signal channel (1-6: LEDs 1-6, 7-12: TTL 1-6)
        """
        channel_index = strict_discrete_range(channel_index, (1, 12), 1)
        self.dll(
            'TU_AddDirectlyTriggeredSignal',
            c_uint8(channel_index))

    def add_generated_tiggered_signal(self, channel_index, t_active,
                                      t_inactive, delay=0,
                                      repitition_count=0,
                                      active_low=False):
        """This function programs a signal of timing unit.
        This signal is generated by the timing unit after an external
        trigger. The trigger input has to be set with command
        :meth:`TU_add_trigger_point`.
        After the trigger input signal the output signal will wait
        for 'start delay' then will be 'active' for 'active time' then
        will be 'inactive' for 'inactive time'. When 'repition count'
        is set so that the signal shall be repeated, the signal will
        again be 'active' for 'active time', 'inactive' for
        'inactive time' and so on until the programmed number
        of repititions is elapsed.

        :param channel_index: signal channel (1-6: LEDs 1-6, 7-12: TTL 1-6)
        :param t_active: active time of the signal [us]
        :param t_inactive: inactive time of the signal [us]
        :param delay: start delay, defaults to 0 us
        :param repitition_count: number of repititions of the signal,
                                 defaults to 0 (infinite)
        :param active_low: polarity of the output signal,
                           defaults to False (active high)
        """
        channel_index = strict_discrete_range(channel_index, (1, 12), 1)
        (t_active, t_inactive, delay, repitition_count) = tuple(
            strict_discrete_range(value, (0, 4294967295), 5)
            for value in (t_active, t_inactive, delay, repitition_count))
        self.dll(
            'TU_AddGeneratedTriggeredSignal',
            c_uint8(channel_index), c_bool(active_low), c_uint32(delay),
            c_uint32(t_active), c_uint32(t_inactive),
            c_uint32(repitition_count))

    def add_trigger_point(self, input_channel, affected_signal_bitmask,
                          starts_low=False, edge_count=1):
        """This function programs a trigger point of the timing unit.
        A trigger point triggers one ore more of the signals programmed
        previously (!) with one of the commands:

            - :meth:`add_generated_tiggered_signal`
            - :meth:`add_directly_triggered_signal`

        When the trigger conditions programmed with this command are met
        the programmend output signals will react accordingly.

        :param input_channel: input trigger channel number
                              (1-6: LEDs 1-6, 7-12: TTL 1-6)
        :param affected_signal_bitmask: bitmask for selecting affected
                                        output channels
        :param starts_low: select polarity of the input signal,
                           defaults to False
        :param edge_count: number of input signal edges before trigger
                           is issued, defaults to 1
        """
        input_channel = strict_discrete_range(input_channel, (1, 12), 1)
        edge_count = strict_range(edge_count, (1, 4294967295))
        affected_signal_bitmask = strict_range(
            affected_signal_bitmask, (1, 4095))
        self.dll(
            'TU_AddTriggerPoint',
            c_uint8(input_channel), c_bool(starts_low), c_uint32(edge_count),
            c_int16(affected_signal_bitmask))

    def add_self_running_signal(self, channel_index, t_active, t_inactive,
                                delay=0, repitition_count=0,
                                active_low=False):
        """This function programs a signal of timing unit.
        This signal is generated by the timing unit itself and does
        not use an external trigger. The start trigger for the sequence
        is done by sending command :meth:`start_stop_output`.
        Signals 1 ... 6 represent the LEDs 1 ... 6.
        Signals 7 ... 12 represent the TTL outputs 1 ... 6.
        This timing unit runs with a resolution of 5us and internal
        32-bit counters.
        Due to this limitation all time values have a maximum
        value of 4.294.967.295 us.
        All time inputs have to be a multiple of 5us.

        Note: 4.294.967.295 us represents a time of a little
        more than 1 hour and 11 minutes.

        :param channel_index: signal channel (1-6: LEDs 1-6, 7-12: TTL 1-6)
        :param t_active: active time of the signal [us]
        :param t_inactive: inactive time of the signal [us]
        :param delay: start delay, defaults to 0 us
        :param repitition_count: number of repititions of the signal,
                                 defaults to 0 (infinite)
        :param active_low: polarity of the output signal,
                           defaults to False (active high)
        """
        channel_index = strict_discrete_range(channel_index, (1, 12), 1)
        (t_active, t_inactive, delay, repitition_count) = tuple(
            strict_discrete_range(value, (0, 4294967295), 5)
            for value in (t_active, t_inactive, delay, repitition_count))
        self.dll(
            'TU_AddGeneratedSelfRunningSignal',
            c_uint8(channel_index), c_bool(active_low), c_uint32(delay),
            c_uint32(t_active), c_uint32(t_inactive),
            c_uint32(repitition_count))

    def start_stop_output(self, start):
        """Start/Stop the timing unit generator.

        :param start: whether to start
        :type start: bool
        """
        self.dll(
            'TU_StartStopGeneratorOutput_TU',
            c_bool(start))

    @staticmethod
    def signal_bitmask(enable_list):
        """Generate bitmask (integer value) from list of booleans.

        :param enable_list: either 6 (LEDs only) or 12 (LEDs + AUX) elements
        """
        if len(enable_list) not in (6, 12):
            raise ValueError(
                'List of channels must have 6 or 12 entries.')
        enable_list = [strict_discrete_set(v, (True, False, 0, 1))
                       for v in enable_list]
        bitmask = 0
        for i, value in enumerate(enable_list):
            if bool(value) is True:
                bitmask += 2**i
        return bitmask
