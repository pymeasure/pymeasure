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

import logging
import time
import re
from ctypes import (cdll, create_string_buffer, c_uint8, c_uint16, c_uint32,
                    c_int16, c_int32, c_char_p, c_wchar_p, c_bool, c_double,
                    byref)
from pymeasure.instruments.validators import (strict_range,
                                              strict_discrete_set,
                                              strict_discrete_range)
from pymeasure.instruments.thorlabs import ThorlabsDLLInstrument

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# compatible devices according to
# https://www.thorlabs.com/software_pages/viewsoftwarepage.cfm?code=OPM
DEVICE_MODELS = [
    'PM100A',
    'PM100D',
    'PM100USB',
    'PM101[AUR]?',
    'PM102[AU]?',
    r'PM16-\d\d\d',
    'PM160',
    'PM160T',
    'PM160T-HP',
    'PM200',
    'PM400'
]


class _ThorlabsPowermeterBase():
    """Base class to inherit further supporting
    instrument classes from. Provides interface
    to the insturment adapter via
    :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    and :meth:`~dll_indexed` methods.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    def __init__(self, dll=None):
        if dll is not None:
            self.dll = dll

    def dll_indexed(self, command, index, c_type=c_double):
        """Pass command and index to the instrument
        to return response.

        :param command: function to call
        :type command: str
        :param index: index property to retrieve
        :type index: int
        :param c_type: c_type of the property, defaults to `c_double`
        :type c_type: c_type, optional
        :return: response value
        :rtype: float
        """
        att = c_type()
        self.dll(command, c_int16(int(index)), byref(att))
        return att.value

    def write(self, command):
        """Write SCPI command to the instrument.

        :param command: command
        :type command: str
        """
        self.dll('writeRaw', c_char_p(command.encode('ascii')))

    def read(self, buffer_size=256):
        """Read directly from the instrument. Make sure
        buffer is long enough for response.

        :param buffer_size: size of buffer, defaults to 256
        :type buffer_size: int, optional
        :return: response string
        :rtype: str
        """
        buffer = create_string_buffer(buffer_size)
        count = c_uint32()
        self.dll('readRaw', byref(buffer), c_uint32(buffer_size), byref(count))
        if count.value >= buffer_size:
            log.warning(
                'Response (lengt: {}) longer'.format(count.value) +
                ' than provided buffer(length: {}),'.format(buffer_size) +
                ' will be truncated.')
        return buffer.value.decode('ascii').strip()

    def ask(self, command, buffer_size=256):
        """Issue SCPI command and read response.

        :param command: SCPI command
        :type command: str
        :param buffer_size: response buffer size, defaults to 256
        :type buffer_size: int, optional
        :return: response string
        :rtype: str
        """
        self.write(command)
        return self.read(buffer_size)

    def _preset_min_max_values(self, property_name, value, default=True):
        """Allows to pass `'MIN'/'MAX'/'DEFAULT'` as
        value specification for a property.
        Checks if value is within range.
        Returns numerical value to pass to instrument.

        :param property_name: name of property
        :type property_name: str
        :param value: value to set
        :type value: str or numeric
        :return: numerical value
        """
        if isinstance(value, str):
            allowed = ('min', 'max')
            if default:
                allowed += ('default',)
            value = strict_discrete_set(value.lower(), allowed)
            value = getattr(self, '{}_{}'.format(property_name, value))
        value = strict_range(value, (
            getattr(self, '{}_min'.format(property_name)),
            getattr(self, '{}_max'.format(property_name))
            ))
        return value


class ThorlabsPowermeter(ThorlabsDLLInstrument, _ThorlabsPowermeterBase):
    """Thorlabs power meter driver based on `TLPM.dll` (libusb).
    This is the same driver as used with the Thorlabs Optical
    Power Monitor v2.0 and above software.

    Remark: Not all models support all the implemented methods.
    Please check the code and the documentation by Thorlabs.

    :param adapter: Thorlabs `TLPM.dll` driver instance
    :type adapter: :class:`~pymeasure.instruments.thorlabs.ThorlabsDLLAdapter`
    :param resourceName: resource name of the instrument
    :type resourceName: str
    :param name: name of the instrument for logging etc.
    :type name: str
    :param id_query: perform ID query during initialization,
                     defaults to True
    :type id_query: bool, optional
    :param reset: reset instrument during initialization,
                  defaults to False
    :type reset: bool, optional
    """
    def __init__(self, adapter, resourceName, name,
                 id_query=True, reset=False):
        ThorlabsDLLInstrument.__init__(
            self, adapter, resourceName, name,
            id_query, reset)
        _ThorlabsPowermeterBase.__init__(self, dll=None)
        self.id
        self.sensor_info
        if self.sensor_type is 'Photodiode':
            self.sensor = _Photodiode(self)
        elif self.sensor_type is 'Thermopile':
            self.sensor = _Thermopile(self)
        elif self.sensor_type is 'Pyroelectric':
            self.sensor = _Pyrosensor(self)
        else:
            log.warning(
                '{}: No sensor configured.'.format(self.name))
        if self.is_power:
            self.power = _PowerMeasurement(self.dll)
            self.voltage = _VoltageMeasurement(self.dll)
            self.current = _CurrentMeasurement(self.dll)
        if self.is_energy:
            self.energy = _EnergyMeasurement(self.dll)
            self.frequency = _FrequencyMeasurement(self.dll)
        if self.model in ['PM200', 'PM400']:
            self.AuxAD0 = _AuxAD(self.dll, 0)
            self.AuxAD1 = _AuxAD(self.dll, 1)
            self.DigitalIO = _DigitalIO(self.dll)
        if self.model is 'PM400':
            self.temperature = _ExternalNTC(self.dll)

    @property
    def sensor_info(self):
        """Read sensor information.
        Sets flags according to sensor capabilities.

        :return: information
        :rtype: dict
        """
        name = create_string_buffer(256)
        SN = create_string_buffer(256)
        calibration = create_string_buffer(256)
        sensor_type = c_int16()
        sensor_subtype = c_int16()
        flags = c_int16()
        self.dll(
            'getSensorInfo', byref(name), byref(SN), byref(calibration),
            byref(sensor_type), byref(sensor_subtype), byref(flags))
        (name, SN, calibration) = tuple(
            x.value.decode('ascii').strip()
            for x in (name, SN, calibration))
        self.sensor_name = name
        types = {
            '0x00': None,
            '0x01': 'Photodiode',
            '0x02': 'Thermopile',
            '0x03': 'Pyroelectric'
            }
        types = {int(k, 0): v for k, v in types.items()}
        self.sensor_type = types[sensor_type.value]
        if self.sensor_type is not None:
            subtypes = {
                '0x00': 'no sensor',
                '0x01': ' adapter',
                '0x02': ' sensor',
                '0x03': ' sensor with integrated filter',
                '0x12': ' sensor with temperature sensor',
                }
            subtypes = {int(k, 0): v for k, v in subtypes.items()}
            self.sensor_subtype = (
                self.sensor_type + subtypes[sensor_subtype.value])
        else:
            self.sensor_subtype = None

        # interpretation of the flags
        # rough trick using bin repr, maybe something more elegant exixts
        # (bitshift, bitarray?)
        # force representation as 9bits, max. value is 371 (sum of all codes)
        self._flags = '{0:09b}'.format(int(flags.value))
        # convert to boolean
        self._flags = tuple(map(lambda x: x == '1', self._flags))
        self._flags = reversed(self._flags)  # account for bit order
        # setting the flags; _dn are empty
        # PM100D_SENS_FLAG_IS_POWER     0x0001 // Power sensor
        # PM100D_SENS_FLAG_IS_ENERGY    0x0002 // Energy sensor
        # PM100D_SENS_FLAG_IS_RESP_SET  0x0010 // Responsivity settable
        # PM100D_SENS_FLAG_IS_WAVEL_SET 0x0020 // Wavelength settable
        # PM100D_SENS_FLAG_IS_TAU_SET   0x0040 // Time constant settable
        # PM100D_SENS_FLAG_HAS_TEMP     0x0100 // With Temperature sensor
        self.is_power, self.is_energy, _d4, _d8, \
            self.resp_settable, self.wavelength_settable, \
            self.tau_settable, _d128, self.temperature_sensor = self._flags
        return {
            "Sensor Name": self.sensor_name,
            "Serial Number": SN,
            "Calibration Message": calibration,
            "Sensor Type": self.sensor_type,
            "Sensor Subtype": self.sensor_subtype,
            "Power Sensor": self.is_power,
            "Energy Sensor": self.is_energy,
            "Responsivity settable": self.resp_settable,
            "Wavelength settable": self.wavelength_settable,
            "Time Constant settable": self.tau_settable,
            "Temperature Sensor": self.temperature_sensor
            }

    @property
    def id(self):
        """Return device identification information.

        :return: Manufacturer, Device Name, Serial Number,
                 Firmware Revision
        :rtype: dict
        """
        device = create_string_buffer(256)
        SN = create_string_buffer(256)
        manufacturer = create_string_buffer(256)
        fwRev = create_string_buffer(256)
        self.dll(
            'identificationQuery',
            byref(manufacturer), byref(device),
            byref(SN), byref(fwRev))
        (device, SN, manufacturer, fwRev) = tuple(
            x.value.decode('ascii').strip()
            for x in (device, SN, manufacturer, fwRev))
        self.model = device
        return {
            "Manufacturer": manufacturer,
            "Device Name": device,
            "Serial Number": SN,
            "Firmware Revision": fwRev
            }

    @property
    def model(self):
        """Device model set via `id` property."""
        return self._model

    @model.setter
    def model(self, model):
        regexes = [re.compile(i) for i in DEVICE_MODELS]
        if not any(regex.match(model) for regex in regexes):
            raise ValueError(
                'Device {} not known or not supported.'.format(model)
                )
        self._model = model

    @property
    def timeout(self):
        """Communication timeout value in [ms]."""
        time = c_uint32()
        self.dll('getTimeoutValue', byref(time))
        return time.value

    @timeout.setter
    def timeout(self, timeout):
        self.dll('setTimeoutValue', c_uint32(int(timeout)))

    #  only available on PM100D, PM100A, PM100USB, PM200, PM400
    @property
    def input_adapter_type(self):
        """Sets the sensor type to assume for custom sensors
        without calibration data memory.
        (Photodiode, Thermopile or Pyroelectric)
        """
        sensor_type = c_int16()
        self.dll('getInputAdapterType', byref(sensor_type))
        sensor_type = {
            1: 'Photodiode Sensor',
            2: 'Thermopile Sensor',
            3: 'Pyroelectric Sensor'}[sensor_type.value]
        return sensor_type

    @input_adapter_type.setter
    def input_adapter_type(self, sensor_type):
        if isinstance(sensor_type, str):
            if 'PHOTODIODE' in sensor_type.upper():
                sensor_type = 1
            elif 'THERMOPILE' in sensor_type.upper():
                sensor_type = 2
            elif 'PYROELECTRIC' in sensor_type.upper():
                sensor_type = 3
            else:
                log.warning(
                    'Sensor type {} not known.'.format(sensor_type))
                return
        sensor_type = strict_discrete_set(sensor_type, (1, 2, 3))
        self.dll('setInputAdapterType', c_int16(sensor_type))

    # average_count: PM100A, PM100D, PM100USB, PM200, PM400
    @property
    def average_count(self):
        """This function sets the average count for
        measurement value generation.

        Notes: The function is deprecated and kept for legacy
        reasons. Its recommended to use :meth:`average_time`
        instead.

        :return: average count
        :rtype: int
        """
        count = c_int16()
        self.dll('getAvgCnt', byref(count))
        return count.value

    @average_count.setter
    def average_count(self, count):
        self.dll('setAvgCnt', c_int16(int(count)))

    @property
    def average_time_min(self):
        """Minimum average time for measurement value generation.
        """
        return self.dll_indexed('getAvgTime', 1)

    @property
    def average_time_max(self):
        """Maximum average time for measurement value generation.
        """
        return self.dll_indexed('getAvgTime', 2)

    @property
    def average_time_default(self):
        """Default average time for measurement value generation.
        """
        return self.dll_indexed('getAvgTime', 3)

    @property
    def average_time(self):
        """Average time for measurement value generation.
        (set: also `'MIN'/'MAX'/'DEFAULT' possible`)
        """
        return self.dll_indexed('getAvgTime', 0)

    @average_time.setter
    def average_time(self, time):
        time = self._preset_min_max_values('average_time', time)
        self.dll('setAvgTime', c_double(time))

    # Attenuation: PM100A, PM100D, PM100USB, PM200, PM400
    @property
    def attenuation_min(self):
        """Minimum settable input attenuation in [dB]."""
        return self.dll_indexed('getAttenuation', 1)

    @property
    def attenuation_max(self):
        """Maximum settable input attenuation in [dB]."""
        return self.dll_indexed('getAttenuation', 2)

    @property
    def attenuation_default(self):
        """Default input attenuation in [dB]."""
        return self.dll_indexed('getAttenuation', 3)

    @property
    def attenuation(self):
        """Input attenuation in [dB].
        (set: also `'MIN'/'MAX'/'DEFAULT' possible`)
        """
        return self.dll_indexed('getAttenuation', 0)

    @attenuation.setter
    def attenuation(self, att):
        att = self._preset_min_max_values('attenuation', att)
        self.dll('setAttenuation', c_double(att))

    # beam diameter:  only available on PM100A, PM100D, PM100USB, PM200, PM400
    @property
    def beam_diameter_min(self):
        """Minimum settable beam diameter in [mm]."""
        return self.dll_indexed('getBeamDia', 1)

    @property
    def beam_diameter_max(self):
        """Maximum settable beam diameter in [mm]."""
        return self.dll_indexed('getBeamDia', 2)

    @property
    def beam_diameter(self):
        """Beam diameter in [mm].
        (set: also `'MIN'/'MAX'/'DEFAULT' possible`)
        """
        return self.dll_indexed('getBeamDia', 0)

    @beam_diameter.setter
    def beam_diameter(self, dia):
        dia = self._preset_min_max_values(
            'beam_diameter', dia, default=False)
        self.dll('setBeamDia', c_double(dia))

    @property
    def wavelength_min(self):
        """Minimum settable wavelength in [nm]."""
        return self.dll_indexed('getWavelength', 1)

    @property
    def wavelength_max(self):
        """Maximum settable wavelength in [nm]."""
        return self.dll_indexed('getWavelength', 2)

    @property
    def wavelength(self):
        """Wavelength in nm."""
        return self.dll_indexed('getWavelength', 0)

    @wavelength.setter
    def wavelength(self, wavelength):
        wavelength = strict_range(
            wavelength, (self.wavelength_min, self.wavelength_max))
        self.dll('setWavelength', c_double(wavelength))

    def dark_adjust(self, timeout=60):
        """This function starts the dark current/zero
        offset adjustment procedure.

        Remark:

            1. You have to darken the input before
            starting dark/zero adjustment.

            2. You can get the state of dark/zero adjustment
            with <Get Dark Adjustment State>

            3. You can stop dark/zero adjustment with
            <Cancel Dark Adjustment>

            4. You get the dark/zero value
            with <Get Dark Offset>

            5. Energy sensors do not support
            this function
        """
        self.dll('startDarkAdjust')
        start = time.time()
        while self._dark_adjust_state is 1:
            if time.time() > start + timeout:
                self.dll('cancelDarkAdjust')
                log.info(
                    "Aborted zero adjustment for %s due to timeout."
                    % self.name)
            else:
                time.sleep(0.5)

    @property
    def _dark_adjust_state(self):
        """This function returns the state of a dark current/zero offset
        adjustment procedure previously initiated by :meth:`dark_adjust`.

        :return: 0: no dark adjustment running
        :rtype: int
        """
        state = c_int16()
        self.dll('getDarkAdjustState', byref(state))
        return state.value

    # not supported for energy sensors
    @property
    def dark_offset(self):
        """Returns the dark/zero offset.
        The unit of the returned offset value depends on the sensor type.
        Photodiodes return the dark offset in ampere [A].
        Thermal sensors return the dark offset in volt [V].

        :return: dark offset
        :rtype: float
        """
        offset = c_double()
        self.dll('getDarkOffset', byref(offset))
        return offset.value

# ---------------------------------------------------------------
# Sensor classes
# ---------------------------------------------------------------


class _ThorlabsPhotosensor(_ThorlabsPowermeterBase):
    """Base class to inherit different sensor types from.
    Provide methods common to all sensor types.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    :param sensor_type: type of sensor
    :type sensor_type: str
    """
    def __init__(self, dll, sensor_type):
        super().__init__(dll)
        sensor_type = strict_discrete_set(
            sensor_type.title(),
            ('Photodiode', 'Thermopile', 'Pyrosensor'))
        self.sensor = sensor_type

    # PD responsivity: only on PM100A, PM100D, PM100USB, PM200, PM400.
    @property
    def responsivity_min(self):
        """Minimum settable responsivity."""
        return self.dll_indexed('get{}Responsivity'.format(self.sensor), 1)

    @property
    def responsivity_max(self):
        """Maximum settable responsivity."""
        return self.dll_indexed('get{}Responsivity'.format(self.sensor), 2)

    @property
    def responsivity_default(self):
        """Default responsivity."""
        return self.dll_indexed(
            'get{}Responsivity'.format(self.sensor), 3)

    @property
    def responsivity(self):
        """Responsivity in
        [A/W], [V/W] or [A/J] depending on sensor type.
        """
        return self.dll_indexed(
            'get{}Responsivity'.format(self.sensor), 0)

    @responsivity.setter
    def responsivity(self, responsivity):
        responsivity = strict_range(
            responsivity, (self.responsivity_min, self.responsivity_max))
        self.dll(
            'set{}Responsivity'.format(self.sensor),
            c_double(responsivity))


class _Photodiode(_ThorlabsPhotosensor):
    """Provides properties and settings of a photodiode sensor.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    def __init__(self, dll):
        super().__init__(dll, 'Photodiode')

    # input filter: only on PM100D, PM100A, PM100USB, PM200, PM400
    @property
    def input_filter(self):
        """Bandwidth filter of the photodiode input stage.
        True enables the lowpass filter."""
        state = c_bool()
        self.dll('getInputFilterState', byref(state))
        return state.value

    @input_filter.setter
    def input_filter(self, toggle):
        self.dll('setInputFilterState', c_bool(toggle))


class _Thermopile(_ThorlabsPhotosensor):
    """Provides properties and settings of a thermopile sensor.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    def __init__(self, dll):
        super().__init__(dll, 'Thermopile')

    # Responsivity: only on PM100A, PM100D, PM100USB, PM160T, PM200, PM400

    # AccelState: only on PM100D, PM100A, PM100USB, PM160T, PM200, PM400
    @property
    def acceleration_state(self):
        """Thermopile acceleration state."""
        state = c_bool()
        self.dll('getAccelState', byref(state))

    @acceleration_state.setter
    def acceleration_state(self, toggle):
        self.dll('setAccelState', c_bool(toggle))

    @property
    def acceleration_mode(self):
        """Thermopile auto acceleration mode.
        `True` corresponds to Auto
        """
        state = c_bool()
        self.dll('getAccelMode', byref(state))

    @acceleration_mode.setter
    def acceleration_mode(self, toggle):
        self.dll('setAccelMode', c_bool(toggle))

    @property
    def acceleration_tau_min(self):
        """Minimum thermopile acceleration time
        constant in seconds [s]"""
        return self.dll_indexed('getAccelTau', 1)

    @property
    def acceleration_tau_max(self):
        """Maximum thermopile acceleration time
        constant in seconds [s]"""
        return self.dll_indexed('getAccelTau', 2)

    @property
    def acceleration_tau_default(self):
        """Default thermopile acceleration time constant in seconds [s]"""
        return self.dll_indexed('getAccelTau', 3)

    @property
    def acceleration_tau(self):
        """Thermopile acceleration time constant in seconds [s]"""
        return self.dll_indexed('getAccelTau', 0)

    @acceleration_tau.setter
    def acceleration_tau(self, tau):
        tau = strict_range(
            tau,
            (self.acceleration_tau_min, self.acceleration_tau_max))
        self.dll('setAccelTau', c_double(tau))


class _Pyrosensor(_ThorlabsPhotosensor):
    """Provides properties and settings of a pyroelectric sensor.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    # Pyrosensor: only available on PM100A, PM100D, PM100USB, PM200, PM400
    def __init__(self, dll):
        super().__init__(dll, 'Pyrosensor')

# ---------------------------------------------------------------
# Measurement classes
# ---------------------------------------------------------------


class _ThorlabsPhotosensorMeasurement(_ThorlabsPowermeterBase):
    """Base class to inherit measurement classes from.
    Provides methods common to (almost) all
    measurement types.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    :param meas_type: type of measurement required
                        as command prefix
    :type meas_type: str
    """
    def __init__(self, dll, meas_type):
        super().__init__(dll)
        meas_type = strict_discrete_set(
            meas_type.title(),
            ('Energy', 'Current', 'Voltage', 'Power'))
        self.meas_type = meas_type

    @property
    def range_min(self):
        """Minimum settable measurement range."""
        return self.dll_indexed('get{}Range'.format(self.meas_type), 1)

    @property
    def range_max(self):
        """Maximum settable measurement range."""
        return self.dll_indexed('get{}Range'.format(self.meas_type), 2)

    @property
    def range(self):
        """Measurement Range (set: also `'MIN'/'MAX'/'DEFAULT` possible)"""
        return self.dll_indexed('get{}Range'.format(self.meas_type), 0)

    @range.setter
    def range(self, value):
        value = self._preset_min_max_values('range', value)
        self.dll('set{}Range'.format(self.meas_type), c_double(value))

    @property
    def reference_min(self):
        """Minimum settable reference Value"""
        return self.dll_indexed('get{}Ref'.format(self.meas_type), 1)

    @property
    def reference_max(self):
        """Maximum settable reference Value"""
        return self.dll_indexed('get{}Ref'.format(self.meas_type), 2)

    @property
    def reference_default(self):
        """Default reference Value"""
        return self.dll_indexed('get{}Ref'.format(self.meas_type), 3)

    @property
    def reference(self):
        """Reference Value (set: also `'MIN'/'MAX'/'DEFAULT'` possible)"""
        return self.dll_indexed('get{}Ref'.format(self.meas_type), 0)

    @reference.setter
    def reference(self, value):
        value = self._preset_min_max_values('reference', value)
        self.dll('set{}Ref'.format(self.meas_type), c_double(value))

    @property
    def reference_state(self):
        """Reference state of the instrument.
        If `True`, relative measurement,
        otherwise absolute measruement.
        """
        state = c_bool()
        self.dll('get{}RefState'.format(self.meas_type), byref(state))
        return state.value

    @reference_state.setter
    def reference_state(self, toggle):
        self.dll('set{}RefState'.format(self.meas_type), c_bool(toggle))

    @property
    def measure(self):
        """Perform measurement"""
        val = c_double()
        self.dll('meas{}'.format(self.meas_type), byref(val))
        return val.value


class _ThorlabsPhotosensorMeasurementAutoRange(
        _ThorlabsPhotosensorMeasurement):
    """Base class to inherit measurement classes from,
    which provide auto ranging.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    :param meas_type: type of measurement required
                        as command prefix
    :type meas_type: str
    """
    @property
    def auto_range(self):
        """Autoranging of the measurement mode."""
        state = c_bool()
        self.dll('get{}AutoRange'.format(self.meas_type), byref(state))
        return state.value

    @auto_range.setter
    def auto_range(self, toggle):
        self.dll('set{}AutoRange'.format(self.meas_type), c_bool(toggle))


class _EnergyMeasurement(_ThorlabsPhotosensorMeasurement):
    """Provides methods for energy measurement and
    related settings.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    def __init__(self, dll):
        super().__init__(dll, 'Energy')

    # only available on PM100D, PM100USB, PM200, PM400
    @property
    def measure_density(self):
        """Energy Density, in J/cm2"""
        val = c_double()
        self.dll('measEnergyDens', byref(val))
        return val.value


class _CurrentMeasurement(_ThorlabsPhotosensorMeasurementAutoRange):
    """Provides methods for current measurement and
    related settings.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    def __init__(self, dll):
        super().__init__(dll, 'Current')

    # measure: only available on PM100D, PM100A, PM100USB, PM160, PM200, PM400


class _VoltageMeasurement(_ThorlabsPhotosensorMeasurementAutoRange):
    """Provides methods for voltage measurement and
    related settings.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    def __init__(self, dll):
        super().__init__(dll, 'Voltage')

    # measure: only available on PM100D, PM100A, PM100USB, PM160T, PM200, PM400


class _PowerMeasurement(_ThorlabsPhotosensorMeasurementAutoRange):
    """Provides methods for power measurement and
    related settings.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    def __init__(self, dll):
        super().__init__(dll, 'Power')

    @property
    def power_unit(self):
        unit = c_int16()
        self.dll('get{}PowerUnit'.format(self.meas_type), byref(unit))
        unit = {0: 'W', 1: 'dBm'}[unit.value]
        return unit

    @power_unit.setter
    def power_unit(self, unit):
        if isinstance(unit, str):
            unit = unit.upper()
            unit = strict_discrete_set(unit, ('W', 'DBM'))
            unit = {'W': 0, 'DBM': 1}[unit]
        unit = strict_discrete_set(int(unit), (0, 1))
        self.dll('set{}PowerUnit'.format(self.meas_type), c_int16(unit))

    # only available on PM100D, PM100A, PM100USB, PM200, PM400
    @property
    def measure_density(self):
        """Power Density, in W/cm2"""
        val = c_double()
        self.dll('measPowerDens', byref(val))
        return val.value


class _FrequencyMeasurement(_ThorlabsPowermeterBase):
    """Provides methods for frequency measurement and
    related settings.

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    # only available on PM100D, PM100A, and PM100USB.
    @property
    def frequency_range(self):
        """The instruments frequency measurement range.

        Remark:
        The frequency of the input signal is calculated over
        at least 0.3s. So it takes at least 0.3s to get a
        new frequency value from the instrument.

        :return: lower and upper frequency in [Hz]
        :rtype: tuple
        """
        lower = c_double()
        upper = c_double()
        self.dll('getFreqRange', byref(lower), byref(upper))
        return (lower.value, upper.value)

    # only available on PM100D, PM100A, PM100USB, PM200, PM400
    @property
    def measure(self):
        """Frequency, in Hz"""
        val = c_double()
        self.dll('measFrequency', byref(val))
        return val.value


class _ExternalNTC(_ThorlabsPowermeterBase):
    """Provides methods for temperature measurement
    with an external NTC sensor and
    related settings. (only PM400)

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """
    # only available on PM400
    def _coefficients(self, index):
        r0 = c_double()
        beta = c_double()
        self.dll(
            'getExtNtcParameter', c_int16(int(index)),
            byref(r0), byref(beta))
        return (r0.value, beta.value)

    @property
    def coefficients_min(self):
        """Minimum temperature calculation coefficients for the
        external NTC sensor."""
        return self.coefficients(1)

    @property
    def coefficients_max(self):
        """Maximum temperature calculation coefficients for the
        external NTC sensor."""
        return self.coefficients(2)

    @property
    def coefficients_default(self):
        """Default temperature calculation coefficients for the
        external NTC sensor."""
        return self.coefficients(3)

    @property
    def coefficients(self):
        """Temperature calculation coefficients for the
        external NTC sensor.

        :return: R0 in [Ohm], beta in [K]
        :rtype: tuple
        """
        return self.coefficients(0)

    @coefficients.setter
    def coefficients(self, values):
        values = [
            strict_range(
                v, (self.coefficients_min[i], self.coefficients_max[i]))
            for i, v in enumerate(values)]
        self.dll(
            'setExtNtcParameter',
            c_double(values[0]),
            c_double(values[1])
            )

    @property
    def measure_resistance(self):
        """Resistance, in [Ohm]"""
        val = c_double()
        self.dll('measExtNtcResistance', byref(val))
        return val.value

    @property
    def measure(self):
        """Temperature, in [°C]"""
        val = c_double()
        self.dll('measExtNtcTemperature', byref(val))
        return val.value


class _AuxAD(_ThorlabsPowermeterBase):
    """Provides methods for measuring voltages at auxiliary
    inputs. (only PM200, PM400)

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    :param channel: index of channel
    :type channel: int
    """
    def __init__(self, dll, channel):
        super().__init__(dll)
        channel = strict_discrete_set(channel, [0, 1])
        self.channel = channel

    @property
    def measure(self):
        """Measure voltage at auxiliary input."""
        val = c_double()
        self.dll('measAuxAD{}'.format(self.channel), byref(val))
        return val.value


class _DigitalIO(_ThorlabsPowermeterBase):
    """Provides methods for digital I/Os. (only PM200, PM400)

    :param dll: dll method of parent instrument, defaults to None
    :type dll:
        :meth:`~pymeasure.instruments.thorlabs.ThorlabsDLLInstrument.dll`
    """

    def _get_4_channel_bool(self, command):
        io0 = c_bool()
        io1 = c_bool()
        io2 = c_bool()
        io3 = c_bool()
        self.dll(
            command,
            byref(io0), byref(io1), byref(io2), byref(io3))
        return tuple([i.value for i in (io0, io1, io2, io3)])

    def _set_4_channel_bool(self, command, value_tuple):
        self.dll(
            'setDigIoDirection',
            c_bool(value_tuple[0]),
            c_bool(value_tuple[1]),
            c_bool(value_tuple[2]),
            c_bool(value_tuple[3])
            )

    @property
    def direction(self):
        """Digital I/O port direction.
        `False` indicates input, `True` indicates output."""
        return self._get_4_channel_bool('getDigIoDirection')

    @direction.setter
    def direction(self, value_tuple):
        self._set_4_channel_bool(
            'setDigIoDirection', value_tuple)

    @property
    def output(self):
        """Digital I/O output state.
        `False` indicates LOW, `True` indicates HIGH.
        """
        return self._get_4_channel_bool('getDigIoOutput')

    @output.setter
    def output(self, value_tuple):
        self._set_4_channel_bool(
            'setDigIoOutput', value_tuple)

    @property
    def port_level(self):
        """Actual digital I/O port level.
        `False` indicates LOW, `True` indicates HIGH.
        """
        return self._get_4_channel_bool('getDigIoPort')
