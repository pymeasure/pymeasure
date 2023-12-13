#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
import pyvisa
import re
import warnings
import time
import numpy as np

from pint import UnitRegistry
from contextlib import contextmanager

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Pint default unit registry
ureg = UnitRegistry()

#############
# Constants #
#############
RAD_TO_COUNTS = 4_608_000/(2*np.pi)     # Based on default INIT-OFFSET values
                                        # and three grating positions on a turret.
MONO_ANGLE_Dv = 0.5432  # [Rad]. monochromator included angle. D_v = (beta - alpha).
                        # Approximate value from DIY measurement.
                        # See: https://www.horiba.com/int/scientific/technologies/diffraction-gratings/diffraction-gratings-ruled-and-holographic/


class PrincetonSP2300i(Instrument):
    """Princeton Instruments SP2300i monochromator-spectrograph.

    Mapping of native commands:
    --------------------
    GOTO        -   > goto (method)
    <GOTO>          x not implemented
    NM              > scanto_locked (method)
    <NM>            x not implemented
    >NM             > scanto (method)
    ?NM             > wavelength (property)
    MONO-?DONE      > is_scanning (property)
    MONO-STOP       > stop_scan (method)
    NM/MON          > scan_rate (property)
    ?NM/MIN         > scan_rate (property)
    GRATING         > grating (property)
    ?GRATING        > grating (property)
    ?GRATINGS       > grating_params (property)
    TURRET          > turrret (property)
    ?TURRET         > turrret (property)
    INSTALL         > install_grating (method)
    SELECT-GRATING  > specify_grating (method)
    G/MM            > specify_line_density (method)
    BLAZE           > specify_blaze (method)
    UNINSTALL       > uninstall_grating (method)
    EXIT-MIRROR     > exit_mirror_pos (propety)
    ENT-MIRROR      x not implemented
    FRONT           x not implemented
    SIDE            x not implemented
    ?MIRROR         x not implemented
    ?MIR            x not implemented
    FRONT-EXIT-SLIT x not implemented
    SIDE-EXIT-SLIT  x not implemented
    FRONT-ENT-SLIT  x not implemented
    SIDE-ENT-SLIT   x not implemented
    MICRONS         x not implemented
    ?MICRONS        x not implemented
    INIT-OFFSET     > init_offset (method)
    INIT-GADJUST    > init_gadjust (method)
    MONO-EESTATUS   > read_eestatus (method)
    RESTORE FACTORY SETTINGS x not implemented
    MONO-RESET      > reset (method)
    HELLO           x not implemented
    MODEL           > model_num (property)
    SERIAL          > serial_num (property)
    INIT-GRATING    > init_grating (method)
    INIT-WAVELENGTH > init_wavelength (method)
    INIT-SRATE      > init_scan_rate (method)

    """

    def __init__(
        self,
        adapter,
        name="Princeton Instruments SP2300i monochromator-spectrograph",
        query_delay=0.02,
        **kwargs
    ):
        kwargs.setdefault('write_termination', '\r')
        kwargs.setdefault('read_termination', '\r\n')
        super().__init__(
            adapter,
            name,
            asrl={
                'baud_rate': 9600,
                'data_bits': 8,
                'stop_bits': pyvisa.constants.StopBits.one,
                'parity': pyvisa.constants.Parity.none,
            },
            **kwargs
        )

        # Read timings
        self.query_delay = query_delay  # [s]
        self._timeout_default = 2000  # [ms]
        self._timeout_movement = 15000  # [ms]  # For commands that initiate movement
        movement_cmds = ['GOTO', ' GRATING']
        self._movement_cmd_pattern = re.compile('|'.join(movement_cmds))

        # Serial connection echos-back
        if self.adapter.connection.interface_type.name == 'asrl':
            self.ECHO_ON = True
        else:
            self.ECHO_ON = False
        self._last_command = ''
        self._read_ok = True

        # Initialize device
        self.adapter.flush_read_buffer()  # Determine if necessary
        self.stop_scan()  # Stop any unterminated scans
        self._scan_stopped = True

    ###############################
    #  Instrument-class Overrides #
    ###############################
    def write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        Updates the _last_command property for use by the read() method.

        :param command: command string to be sent to the instrument
        :param kwargs: Keyword arguments for the adapter.
        """
        self._last_command = command
        super().write(command, **kwargs)

    def read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        Strips the leading echo if using a serial connection and updates
        the _read_ok parameter.

        """
        # Dynamically update read timeout
        if self._movement_cmd_pattern.search(self._last_command):
            self.adapter.connection.timeout = self._timeout_movement

        # Read from instrument
        reply = super().read(**kwargs)

        # Parse command echo, value, and status
        # Echo and leading/trailing whitespace (if present): (\s*{re.escape(self._last_command)}\s*)?
        # Value: (.*?)
        # Status (if present): (ok)? or (\?)?
        match = re.match(f'^\s*({re.escape(self._last_command)})?\s*(.*?)\s*(ok)?(\?)?\s*$', reply)

        # Check read is OK
        if match[3] == 'ok':
            self._read_ok = True
        else:
            self._read_ok = False

        # Reset default timeout
        self.adapter.connection.timeout = self._timeout_default

        return match[2]

    def wait_for(self, query_delay=0):
        """Wait for some time.

        :param query_delay: override the global query_delay.
        """
        super().wait_for(query_delay or self.query_delay)

    def write_bytes(self):
        """Not implemented -- use adapter method."""
        raise NotImplementedError("Use adapter method")

    def read_bytes(self):
        """Not implemented -- use adapter method."""
        raise NotImplementedError("Use adapter method")

    def write_binary_values(self):
        """Not implemented -- use adapter method."""
        raise NotImplementedError("Use adapter method")

    def read_binary_values(self):
        """Not implemented -- use adapter method."""
        raise NotImplementedError("Use adapter method")

    def check_errors(self):
        """Read all errors from the instrument and log them.

        :return: List of error entries.
        """
        errors = []
        if not self._read_ok:
            # IO error
            err = [0, "Communication error. Reset device and flush buffer. "]
            log.error(f"{self.name}: {err[0]}, {err[1]}")
            errors.append(err)
        return errors

    def check_get_errors(self):
        """Check for errors after having gotten a property and log them.

        Called if :code:`check_get_errors=True` is set for that property.

        :return: List of error entries.
        """
        return self.check_errors()

    def check_set_errors(self):
        """Check for errors after having set a property and log them.

        Called if :code:`check_set_errors=True` is set for that property.

        :return: List of error entries.
        """
        self.read()
        return self.check_errors()

    ################
    #  Properties  #
    ################

    # ?NM
    wavelength = Instrument.measurement(
        "?NM", "Returns the current wavelength position [nm].",
        get_process=lambda v: ureg.Quantity(v),  # convert to quantity
    )

    # MONO-?DONE
    is_scanning = Instrument.measurement(
        "MONO-?DONE", "Returns the scanning status.",
        map_values=True,
        values={True: 0, False: 1},
    )

    # NM/MIN
    # ?NM/MIN
    scan_rate = Instrument.control(
        "?NM/MIN", "%0.3f NM/MIN",
        """The scan rate in wavelength/time.

            Set as a pint compatible value.
        """,
        get_process=lambda v: ureg.Quantity(v),  # convert to quantity
        set_process=lambda v: ureg.Quantity(v).m_as('nm/min'),
        check_set_errors=True,
    )

    # GRATING
    # ?GRATING
    grating = Instrument.control(
        "?GRATING", "%d GRATING",
        """The grating being used.

            Gratings are numbered from 1 to 9. The grating number is found as
            follows: grating_num = 3*(turret_num -1) + turret_position. For
            example, the first grating on the installed turret is 1, 4, and 7
            for turrets 1, 2, and 3 respectively.
        """,
        validator=strict_discrete_set,
        values=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        get_process=lambda v: int(v),  # convert to integer
        set_process=lambda v: int(v),
        check_set_errors=True,
    )

    # ?GRATINGS
    @property
    def grating_params(self):
        """A dict of grating parameters.

        Values
            For loaded grating positions: (groves/mm, blaze_wavelength)
            For unloaded grating positions: None
        """
        self.ask('?GRATINGS')
        grating_params = {}
        pattern = re.compile(r'(\d+)\s+([0-9]+ g/mm)\s+BLZ=\s+(.*?)$|(\d+)\s+Not Installed')
        for g in range(1, 10):
            reply = self.read()
            match = pattern.search(reply)
            if match.group(4):
                values = None
                grating_params[int(match.group(4))] = values
            else:
                values = (match.group(2), match.group(3))
                grating_params[int(match.group(1))] = values
        self.check_set_errors()  # Clear 'OK' string from buffer
        return grating_params

    # TURRET
    # ?TURRET
    turret = Instrument.control(
        "?TURRET", "%d TURRET",
        """The turret being used.

            Turrets are numbered from 1 to 3.
        """,
        validator=strict_discrete_set,
        values=[1, 2, 3],
        get_process=lambda v: int(v),  # convert to integer
        set_process=lambda v: int(v),
        check_set_errors=True,
    )

    # EXIT-MIRROR
    @property
    def exit_mirror_pos(self):
        """The exit diverter mirror position.

        This property can have the value "front" or "side"
        """
        self.ask('EXIT-MIRROR')
        pos = self.ask('?MIRROR')
        return pos

    @exit_mirror_pos.setter
    def exit_mirror_pos(self, pos):
        self.ask('EXIT-MIRROR')
        if pos == 'front' or pos == 0:
            self.ask('FRONT')
        elif pos == 'side' or pos == 1:
            self.ask('SIDE')
        else:
            raise ValueError('Possible values: ''front'' or 0, ''side'' or 1')

    # MODEL
    model_num = Instrument.measurement(
        "MODEL", "Returns the model number.",
    )

    # SERIAL
    serial_num = Instrument.measurement(
        "Serial", "Returns the serial number.",
    )

    #############
    #  Methods  #
    #############

    # GOTO
    def goto(self, wl):
        """Jogs to the desired wavelength.

        :param wl: Desired wavelength, pint-compatible value
        """
        if self.is_scanning:
            warnings.warn('Stopping running scan')
        self.stop_scan()  # Stop running or finished scans
        wl = ureg.Quantity(wl).m_as(ureg.nm)  # convert to [nm]
        self.ask(f'{wl:0.3f} GOTO')

    # >NM
    def scanto(self, wl):
        """Scans to the desired wavelength.

        Scanning begins from the current wavelength. The scan should be
        properly terminated with the stop_scan method after calling; however,
        gaurds are in place to always stop an existing scan before moving the
        grating.

        :param wl: Final wavelength of the scan, pint-compatible value
        """
        if self.is_scanning:
            warnings.warn('Stopping running scan')
        self.stop_scan()  # Stop running or finished scans
        wl = ureg.Quantity(wl).m_as(ureg.nm)  # convert to [nm]
        self.ask(f'{wl:0.3f} >NM')

    # NM
    def scanto_locked(self, wl):
        """Scans to the desired wavelength.

        Communication unresponsive until scan completion. Scan automatically
        stopped by instrument.
        """
        if self.is_scanning:
            warnings.warn('Stopping running scan')
        self.stop_scan()  # Stop running or finished scans
        wl = ureg.Quantity(wl).m_as(ureg.nm)  # convert to [nm]
        self.ask(f'{wl:0.3f} NM')

    @contextmanager
    def scanto_context(self, wl):
        """Scans to the desired wavelength.

        Creates a context for scanning that ensures the scan is properly
        stopped. Users can poll wavelength and is_scanning parameters at
        desired frequency.

        :param wl: Final wavelength of the scan, pint-compatible value
        """
        try:
            self.scanto(wl)
            yield
        finally:
            self.stop_scan()

    # MONO-STOP
    def stop_scan(self):
        """ Stops any running scans."""
        self.ask('MONO-STOP')
        if self._read_ok:
            self._scan_stopped = True
        else:
            raise IOError("Communication error. Reset device and flush buffer.")

    # INSTALL
    def install_grating(self, grating_num, acton_part_num):
        """Install a grating with an Acton part number.

        Installs new grating parameters into the non-volatile memory of the
        SP-2300i monochromator. Uses the part number of the grating to
        specify the parameters. e.g., 1-120-500 5 INSTALL places a 1200 g/mm
        grating blazed at 500 nm into the second grating position on turret
        number 2.

        :grating_num: Grating position on the turret
        :acton_part_num: Part number of the installed grating
        """
        self.ask(f'{acton_part_num} {grating_num} INSTALL')

    # SELECT-GRATING
    def specify_grating(self, grating_num):
        """Specify a grating position for parameter editing purposes.

        Specify a desired grating for the purpose of installing/editing its
        parameters in non-volatile memory.

        :grating_num: Grating position on the turret
        """
        self.ask(f'{grating_num} SELECT-GRATING')

    # G/MM
    def specify_line_density(self, grating_num, g_per_mm):
        """Specify the line density of a grating in groves/mm.

        Specifies groove density of grating to be installed in g/mm. e.g.,
        1200 g/mm

        :grating_num: Grating position on the turret.
        :g_per_mm: Number of groves per mm.
        """
        self.specify_grating(grating_num)
        self.ask(f'{g_per_mm} G/MM')

    # BLAZE
    def specify_blaze(self, grating_num, blaze):
        """Specify the blaze wavelength.

        This is a 7-character user-defined label. Typically something like
        8.UM, or 8 um, or 8000 nm.

        :grating_num: Grating position on the turret.
        :blaze: User-defiled label. String.
        """
        self.specify_grating(grating_num)
        self.ask(f'BLAZE')
        self.ask(f'{blaze}')

    # UNINSTALL
    def uninstall_grating(self, grating_num):
        """Uninstall a grating.

        Used to remove a grating and its parameters from the SP-2300i
        non-volatile memory.

        :grating_num: Grating position on the turret
        """
        self.specify_grating(grating_num)
        self.ask(f'UNINSTALL')

    # INIT-OFFSET
    def init_offset(self, grating_num, offset):
        """Specify the grating offset angle in motor counts.

        Sets the offset value for the designated grating. Default values are 0
        for gratings 1, 4 and 7; 1536000 for gratings 2, 5 and 8; and 3072000
        for gratings 3, 6, and 9. The limits on the settings are +/-2500 for a
        1200 g/mm grating. This corresponds to an error of greater than +/- 5
        nm for a 1200 g/mm grating. The limits are adjusted for grating groove
        density, e.g., error for a 600 g/mm grating is +/- 5000. The grating
        number is a value from 1-9, as defined for the <grating> property.

        :grating_num: Grating position on the turret.
        :offset: Offset in motor counts.
        """
        self.ask(f'{offset:d}. {(grating_num-1):d} INIT-OFFSET')

    def _calc_grating_angle(self, grating_num, wl):
        """The current grating angle.

            The angle of the grating in [Rad] away from the lambda=0 position.

            :grating_num: Grating position on the turret.
            :wl: The wavelength position/setting of the SP2300i [unitful].
        """
        wl = ureg.Quantity(wl).m_as('nm')
        g_per_mm = ureg.Quantity(self.grating_params[grating_num][0]).m_as('g/mm')
        theta = np.arcsin(1e-6*g_per_mm*wl/(2*np.cos(MONO_ANGLE_Dv/2)))
        return theta

    def calc_offset(self, grating_num, wl_known, wl_position):
        """Calculate the grating offset angle in motor counts.

            :grating_num: Grating position on the turret.
            :wl_known: The known wavelength of the calibration source [unitful].
            :wl_position: The required wavelength position/setting of the
                monochromator to center the known wavelength on the output
                slit/array [unitful].
        """
        theta_known = self._calc_grating_angle(grating_num, wl_known)
        theta_position = self._calc_grating_angle(grating_num, wl_position)
        d_theta = theta_position - theta_known
        d_theta_counts = d_theta * RAD_TO_COUNTS
        status = self.read_eestatus()
        offset_match = re.search(
            r'offset\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)',
            status)
        # adjust_match = re.search(
        #     r'adjust\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)',
        #     status)
        return round(int(offset_match[grating_num]) + d_theta_counts)

    # INIT-GADJUST
    def init_gadjust(self, grating_num, gadjust):
        """Specify the grating adjustment scaling factor in motor counts.

        The Gadjust value is a factor used to make fine adjustments to the
        higher wavelengths for a selected grating. Gadjust effectively accounts
        for deviations in the expected angular dispersion of the grating by
        scaling the number of motor counts necessary to rotate the diffracted
        wavelength towards the exit slit. Default parameters are listed in
        grating_params for any grating position for which a grating is not
        installed.

        Note: we are using the INIT-SP300-GADJUST native command, which allows
        Gadjust values in the range 1_000_000 +/- 100_000 =
        [1_100_000, 900_000]. The default value of Gadjust in non-volatile
        memeory is 980_000, not 1_000_000 as suggested in the manual.

        :grating_num: Grating position on the turret.
        :gadjust: Adjustment factor in motor counts.
        """
        strict_range(gadjust, [900_000, 1_100_000])  # Validate user input
        self.write(f'{gadjust:d} {(grating_num-1):d} INIT-SP300-GADJUST')

        timeout = 2  # [s]
        start_time = time.time()
        reply = ''
        while time.time() - start_time < timeout:
            reply += str(
                # Read only the buffer content
                self.adapter.connection.read_bytes(
                    self.adapter.connection.bytes_in_buffer),
                'utf8'
            )
            if re.search('ok\r\n$', reply):
                self._read_ok = True
                break
            elif re.search('bad eeGADJUST$', reply):
                self._read_ok = False
                raise ValueError('gadjust value out of range')
            self.wait_for()
        else:
            raise TimeoutError('Communication error. Reset device and flush buffer.')
        return

    def calc_gadjust(self, grating_num, wl_known, wl_position):
        """Calculate the grating adjustment factor.

            :grating_num: Grating position on the turret.
            :wl_known: The known wavelength of the calibration source [unitful].
            :wl_position: The required wavelength position/setting of the
                monochromator to center the known wavelength on the output
                slit/array [unitful].
        """
        # Find gadjust from a ratio of motor angles/counts
        # theta_known = self._calc_grating_angle(grating_num, wl_known)
        # theta_position = self._calc_grating_angle(grating_num, wl_position)
        # r_theta = theta_known/theta_position

        # Find gadjust from a ratio of wavelengths (as inferred from Figure 9
        # in "Acton Monochromator Control Software for Windows")
        r_wl = ureg.Quantity(wl_known).m_as('nm')/ureg.Quantity(wl_position).m_as('nm')
        status = self.read_eestatus()
        adjust_match = re.search(
            r'adjust\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)',
            status)
        return round(int(adjust_match[grating_num]) * r_wl)

    # MONO-EESTATUS
    def read_eestatus(self):
        self.ask('MONO-EESTATUS')
        status = ''
        while not self._read_ok:
            status += self.read() + '\n'
        return status

    # MONO-RESET
    def reset(self):
        self.ask('MONO-RESET')
        reply = ''
        timeout = 60  # [s]
        start_time = time.time()
        while time.time() - start_time < timeout:
            reply += str(
                self.adapter.connection.read_bytes(
                    self.adapter.connection.bytes_in_buffer,
                    break_on_termchar=True),  # Read only the buffer content
                'utf8'
            )
            if re.search('ok', reply):
                self._read_ok = True
                break
            elif re.search('Homing', reply):
                print(reply)
                reply = ''
            elif re.search(self.adapter.connection.read_termination+'$', reply):
                reply = re.sub(self.adapter.connection.read_termination, '', reply)
                print(reply)  # A complete line has been read
                reply = ''
            self.wait_for()
        else:
            raise TimeoutError('Reset not performed. \
                Possible communication error. Reset device and flush buffer.')
        return

    # INIT-GRATING
    def init_grating(self, grating_num):
        """Specify the initial grating on restart.

        Specifies which of the three gratings on the installed turret the SP-2300i
        will go to after finding 0.0 nm on the first grating of the installed
        turret. Accepts values 1-9.

        :grating_num: Grating position on the turret.
        """
        self.ask(f'{grating_num:d} INIT-GRATING')

    # INIT-WAVELENGTH
    def init_wavelength(self, wl):
        """Specify the initial wavelength on restart.

        Sets an initial wavelength for the SP-2300i after initialization.

        :wl: Wavelength [unitful].
        """
        wl = ureg.Quantity(wl).m_as('nm')  # Convert to [nm]
        self.ask(f'{wl:0.3f} INIT-WAVELENGTH')

    # INIT-SRATE
    def init_scan_rate(self, scan_rate):
        """Specify the initial wavelength on restart.

        Sets an initial wavelength for the SP-2300i after initialization.

        :wl: Wavelength [unitful].
        """
        scan_rate = ureg.Quantity(scan_rate).m_as('nm/min')  # Convert to [nm/min]
        self.ask(f'{scan_rate:0.3f} INIT-SRATE')
