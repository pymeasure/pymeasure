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

from pymeasure.instruments import Instrument
from pymeasure.instruments.teledyne.teledyne_oscilloscope import TeledyneOscilloscope, \
    TeledyneOscilloscopeChannel, _results_list_to_dict

from struct import unpack
from dataclasses import dataclass
import numpy as np
from decimal import Decimal
import re 


def sanitize_source(source):
    """Parse source string.

    :param source: can be "cX", "ch X", "chan X", "channel X", "math" or "line", where X is
    a single digit integer. The parser is case and white space insensitive.
    :return: can be "C1", "C2", "C3", "C4", "MATH" or "LINE.
    """

    match = re.match(r"^\s*(C|CH|CHAN|CHANNEL)\s*(?P<number>\d)\s*$|"
                     r"^\s*(?P<name_only>MATH|LINE)\s*$", source, re.IGNORECASE)
    if match:
        if match.group("number") is not None:
            source = "C" + match.group("number")
        else:
            source = match.group("name_only")
        source = source.upper()
    else:
        raise ValueError(f"source {source} not recognized")
    return source


class _ChunkResizer:
    """The only purpose of this class is to resize the chunk size of the instrument adapter.

    This is necessary when reading a big chunk of data from the oscilloscope like image dumps and
    waveforms.

    .. Note::
        Only if the new chunk size is bigger than the current chunk size, it is resized.

    """

    def __init__(self, adapter, chunk_size):
        """Just initialize the object attributes.

        :param adapter: Adapter of the instrument. This is usually accessed through the
                        Instrument::adapter attribute.
        :param chunk_size: new chunk size (int).
        """
        self.adapter = adapter
        self.old_chunk_size = None
        self.new_chunk_size = int(chunk_size) if chunk_size else 0

    def __enter__(self):
        """Only resize the chunk size if the adapter support this feature."""
        if (self.adapter.connection is not None
                and hasattr(self.adapter.connection, "chunk_size")):
            if self.new_chunk_size > self.adapter.connection.chunk_size:
                self.old_chunk_size = self.adapter.connection.chunk_size
                self.adapter.connection.chunk_size = self.new_chunk_size

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_chunk_size is not None:
            self.adapter.connection.chunk_size = self.old_chunk_size


@dataclass
class MAUIWaveformDescriptor:
    desc_name           : str
    desc_templ_name     : str
    desc_comm_type      : int
    desc_comm_order     : int
    wave_desc_len       : int
    user_txt_len        : int
    trig_time_arr       : int
    ris_time_arr        : int
    wave_arr_1          : int
    wave_arr_2          : int
    instr_name          : str
    instr_num           : int
    trace_label         : str
    wave_arr_count      : int
    pts_per_screen      : int
    first_valid         : int
    last_valid          : int
    first_pt            : int
    sparsing_factor     : int
    segment_num         : int
    subarr_count        : int
    sweeps_per_acq      : int
    pts_per_pair        : int
    pair_offset         : int
    vgain               : float
    vos                 : float
    max_value           : float
    min_value           : float
    nominal_bits        : int
    nom_subarr_count    : int
    horiz_ival          : float
    horiz_os            : int
    pixel_os            : int
    vunit               : str
    hunit               : str
    huncert             : float
    # trigger_time      : struct
    acq_duration        : float
    ca_record_type      : int
    processing_done     : int
    ris_sweeps          : int
    time_base           : int
    vcoupling           : int
    probe_atten         : float
    fixed_vgain         : int
    bwlimit             : int
    vertical_vernier    : float
    acq_vos             : float
    wave_src            : int

    @classmethod
    def parse_desc(cls,desc: bytes):
        """
        Get description with something like this:
            self.write(f"{self.waveform_source}:WF? DESC")
            desc = self.read_bytes(-1)
        Assumes COMM_HEADER == OFF
        """
        # Check for header
        if desc[0:7].decode('ascii') == 'DESC,#9':
            desc = desc[len('DESC,#9000000000'):]  # don't need this

        # parse
        desc_name           = desc[0:16].split(b'\x00',1)[0].decode('ascii')
        desc_templ_name     = desc[16:32].split(b'\x00',1)[0].decode('ascii')
        desc_comm_type      = unpack('<h',desc[32:34])[0]
        desc_comm_order     = unpack('<h',desc[34:36])[0]
        wave_desc_len       = unpack('<l',desc[36:40])[0]
        user_txt_len        = unpack('<l',desc[40:44])[0]
        trig_time_arr       = unpack('<l',desc[48:52])[0]
        ris_time_arr        = unpack('<l',desc[52:56])[0]
        wave_arr_1          = unpack('<l',desc[60:64])[0]
        wave_arr_2          = unpack('<l',desc[64:68])[0]
        instr_name          = desc[76:92].split(b'\x00',1)[0].decode('ascii')
        instr_num           = unpack('<L',desc[92:96])[0]
        trace_label         = desc[96:112].split(b'\x00',1)[0].decode('ascii')
        wave_arr_count      = unpack('<l',desc[116:120])[0]
        pts_per_screen      = unpack('<l',desc[120:124])[0]
        first_valid         = unpack('<l',desc[124:128])[0]
        last_valid          = unpack('<l',desc[128:132])[0]
        first_pt            = unpack('<l',desc[132:136])[0]
        sparsing_factor     = unpack('<l',desc[136:140])[0]
        segment_num         = unpack('<l',desc[140:144])[0]
        subarr_count        = unpack('<l',desc[144:148])[0]
        sweeps_per_acq      = unpack('<l',desc[148:152])[0]
        pts_per_pair        = unpack('<h',desc[152:154])[0]
        pair_offset         = unpack('<h',desc[154:156])[0]
        vgain               = unpack('<f',desc[156:160])[0]  # units/lsb
        vos                 = unpack('<f',desc[160:164])[0]  # offset in volts
        max_value           = unpack('<f',desc[164:168])[0]
        min_value           = unpack('<f',desc[168:172])[0]
        nominal_bits        = unpack('<h',desc[172:174])[0]
        nom_subarr_count    = unpack('<h',desc[174:176])[0]
        horiz_ival          = unpack('<f',desc[176:180])[0]
        horiz_os            = unpack('<d',desc[180:188])[0]
        pixel_os            = unpack('<d',desc[188:196])[0]
        vunit               = desc[196:244].split(b'\x00',1)[0].decode('ascii')
        hunit               = desc[244:296].split(b'\x00',1)[0].decode('ascii')
        huncert             = unpack('<f',desc[292:296])[0]
        # trigger_time        = desc[296:312]    # structure
        acq_duration        = unpack('<f',desc[312:316])[0]
        ca_record_type      = unpack('<h',desc[316:318])[0]
        processing_done     = unpack('<h',desc[318:320])[0]
        ris_sweeps          = unpack('<h',desc[322:324])[0]
        time_base           = unpack('<h',desc[324:326])[0]
        vcoupling           = unpack('<h',desc[326:328])[0]
        probe_atten         = unpack('<f',desc[328:332])[0]
        fixed_vgain         = unpack('<h',desc[332:334])[0]
        bwlimit             = unpack('<h',desc[334:336])[0]
        vertical_vernier    = unpack('<f',desc[336:340])[0]
        acq_vos             = unpack('<f',desc[340:344])[0]
        wave_src            = unpack('<h',desc[344:346])[0]

        return cls(desc_name, desc_templ_name, desc_comm_type, desc_comm_order, wave_desc_len  , user_txt_len   ,
                    trig_time_arr, ris_time_arr, wave_arr_1, wave_arr_2, instr_name,
                    instr_num, trace_label, wave_arr_count, pts_per_screen , first_valid,
                    last_valid, first_pt, sparsing_factor, segment_num, subarr_count,
                    sweeps_per_acq , pts_per_pair, pair_offset, vgain, vos,
                    max_value, min_value, nominal_bits, nom_subarr_count, horiz_ival,
                    horiz_os, pixel_os, vunit, hunit, huncert,
                    acq_duration, ca_record_type , processing_done, ris_sweeps,
                    time_base, vcoupling, probe_atten, fixed_vgain, bwlimit,
                    vertical_vernier, acq_vos, wave_src)


class TeledyneMAUIChannel(TeledyneOscilloscopeChannel):
    """Base class for channels on a :class:`TeledyneMAUI` device."""

    # Probably for historic reasons, "20MHZ" is registered as "ON"
    BANDWIDTH_LIMITS = ["OFF", "ON", "200MHZ"]

    TRIGGER_SLOPES = {"negative": "NEG", "positive": "POS"}

    # Reset listed values for existing commands:
    bwlimit_values = BANDWIDTH_LIMITS

    def autoscale(self):
        """Perform auto-setup command for channel."""
        self.write("AUTO_SETUP FIND")

    # noinspection PyIncorrectDocstring
    def setup(self, **kwargs):
        """Setup channel. Unspecified settings are not modified.

        Modifying values such as probe attenuation will modify offset, range, etc. Refer to
        oscilloscope documentation and make multiple consecutive calls to setup() if needed.
        See property descriptions for more information.

        :param bwlimit:
        :param coupling:
        :param display:
        :param offset:
        :param probe_attenuation:
        :param scale:
        :param trigger_coupling:
        :param trigger_level:
        :param trigger_slope:
        """
        super().setup(**kwargs)

    @property
    def current_configuration(self):
        """Get channel configuration as a dict containing the following keys:

        - "channel": channel number (int)
        - "attenuation": probe attenuation (float)
        - "bandwidth_limit": bandwidth limiting, parsed for this channel (str)
        - "coupling": "ac 1M", "dc 1M", "ground" coupling (str)
        - "offset": vertical offset (float)
        - "display": currently displayed (bool)
        - "volts_div": vertical divisions (float)
        - "trigger_coupling": trigger coupling can be "dc" "ac" "highpass" "lowpass" (str)
        - "trigger_level": trigger level (float)
        - "trigger_slope": trigger slope can be "negative" "positive" "window" (str)
        """
        ch_setup = {
            "channel": self.id,
            "attenuation": self.probe_attenuation,
            "bandwidth_limit": self.bwlimit[f"C{self.id}"],
            "coupling": self.coupling,
            "offset": self.offset,
            "display": self.display,
            "volts_div": self.scale,
            "trigger_coupling": self.trigger_coupling,
            "trigger_level": self.trigger_level,
            "trigger_slope": self.trigger_slope
        }
        return ch_setup


class TeledyneMAUI(TeledyneOscilloscope):
    """A base class for the MAUI-type of Teledyne oscilloscopes.

    This base class works out of the box. Some properties, especially the number of channels,
    might have to be adjusted to the actual device.

    The manual detailing the API is "MAUI Oscilloscopes Remote Control and Automation Manual"
    (`link`_).

    This class of Teledyne oscilloscopes also support direct VBS commands.
    See :meth:`~vbs_ask` and :meth:`~vbs_write`.

    .. _link: https://cdn.teledynelecroy.com/files/manuals/
              maui-remote-control-and-automation-manual.pdf
    """

    ch_1 = Instrument.ChannelCreator(TeledyneMAUIChannel, 1)

    ch_2 = Instrument.ChannelCreator(TeledyneMAUIChannel, 2)

    ch_3 = Instrument.ChannelCreator(TeledyneMAUIChannel, 3)

    ch_4 = Instrument.ChannelCreator(TeledyneMAUIChannel, 4)

    # Change listed values for existing commands:
    bwlimit_values = TeledyneMAUIChannel.BANDWIDTH_LIMITS


    def __init__(self, adapter, name="Teledyne Oscilloscope", **kwargs):
        super().__init__(adapter, name=name, **kwargs)
        self.waveform_descriptor = None

    def vbs_write(self, message: str):
        """Write a VBS command directly to the device.

        This class of oscilloscopes also allows the direct usage of Visual Basic
        Scripting (VBScript). With this method a literal VBS command is sent.
        You can use the 'MAUI Browser' on the oscilloscope to list all available
        variables.

        A very basic example of usage:

        .. code:: python

           instrument.vbs_write("app.Display.GridMode = Dual")
        """
        query = f"VBS '{message}'"
        self.write(query)

    def vbs_ask(self, name: str) -> str:
        """Return the value of a VBS variable.

        Only the target needs to be specified, a query is formatted by this method.
        Note: the target name is not escaped!

        See :meth:`~vbs_write` for more info.

        A very basic example of usage:

        .. code:: python

           instrument.vbs_ask("app.Display.GridMode")
        """
        query = f"VBS? 'Return={name}'"
        return self.ask(query)

    ###############
    #   Trigger   #
    ###############

    @property
    def trigger(self):
        """Get trigger setup as a dict containing the following keys:

        - "mode": trigger sweep mode [auto, normal, single, stop]
        - "trigger_type": condition that will trigger the acquisition of waveforms
          [edge,slew,glit,intv,runt,drop]
        - "source": trigger source [c1,c2,c3,c4]
        - "hold_type": hold type (refer to page 172 of programing guide)
        - "hold_value1": hold value1 (refer to page 172 of programing guide)
        - "hold_value2": hold value2 (refer to page 172 of programing guide)
        - "coupling": input coupling for the selected trigger sources
        - "level": trigger level voltage for the active trigger source
        - "slope": trigger slope of the specified trigger source

        """
        trigger_select = self.trigger_select
        ch = self.ch(trigger_select[1])
        tb_setup = {
            "mode": self.trigger_mode,
            "trigger_type": trigger_select[0],
            "source": trigger_select[1],
            "hold_type": trigger_select[2],
            "hold_value1": trigger_select[3] if len(trigger_select) >= 4 else None,
            "hold_value2": trigger_select[4] if len(trigger_select) >= 5 else None,
            "coupling": ch.trigger_coupling,
            "level": ch.trigger_level,
            "slope": ch.trigger_slope
        }
        return tb_setup

    def force_trigger(self):
        """Make one acquisition if in active trigger mode.

        No action is taken if the device is in 'Stop trigger mode'.
        """
        # Method instead of property since no reply is sent
        self.write("FRTR")

    

    ##################
    #    Waveform    #
    ##################

    def _digitize(self, src, num_bytes=None, block='DAT1'):
        """Acquire waveforms according to the settings of the acquire commands.
        Note.
        If the requested number of bytes is not specified, the default chunk size is used,
        but in such a case it cannot be guaranteed that the message is received in its entirety.

        :param src: source of data: "C1", "C2", "C3", "C4", "MATH".
        :param block: waveform block to be read: "DESC", "TEXT", "TIME", "DAT1", "DAT2"
        :param: num_bytes: number of bytes expected from the scope (including the header and
        footer).
        :return: bytearray with raw data.
        """
        with _ChunkResizer(self.adapter, num_bytes):
            # Get descriptor
            self.write(f"{self.waveform_source}:WF? DESC")
            dd = self.read_bytes(-1)
            descb = dd[len('DESC,#9000000000'):]
            self.waveform_descriptor = MAUIWaveformDescriptor.parse_desc(descb)
            # Get data
            binary_values = self.binary_values(f"{src}:WF? {block}", dtype=np.uint8)
        if num_bytes is not None and len(binary_values) != num_bytes-1:
            raise BufferError(f"read bytes ({len(binary_values)}) != requested bytes ({num_bytes})")
        return binary_values

    def _header_footer_sanity_checks(self, message, block='DAT1'):
        """Check that the header follows the predefined format.
        The format of the header is <block>,#9XXXXXXX where XXXXXXX is the number of acquired
        points, and it is zero padded.
        Then check that the footer is present. The footer is a double line-carriage \n\n
        :param message: raw bytes received from the scope """
        message_header = bytes(message[0:self._header_size]).decode("ascii")
        # Sanity check on header and footer
        if message_header[0:7] != f"{block},#9":
            raise ValueError(f"Waveform data in invalid : header is {message_header}")

    def _npoints_sanity_checks(self, message):
        """Check that the number of transmitted points is consistent with the message length.
        :param message: raw bytes received from the scope """
        message_header = bytes(message[0:self._header_size]).decode("ascii")
        transmitted_points = int(message_header[-9:])
        received_points = len(message) - self._header_size - self._footer_size
        if transmitted_points-1 != received_points:
            raise ValueError(f"Number of transmitted points ({transmitted_points}) != "
                             f"number of received points ({received_points})")

    def _acquire_data(self, requested_points=0, sparsing=1, block='DAT1'):
        """Acquire raw data points from the scope. The header, footer and number of points are
        sanity-checked, but they are not processed otherwise. For a description of the input
        arguments refer to the download_waveform method.
        If the number of expected points is big enough, the transmission is split in smaller
        chunks of 20k points and read one chunk at a time. I do not know the reason why,
        but if the chunk size is big enough the transmission does not complete successfully.
        :return: raw data points as numpy array and waveform preamble
        """
        # Setup waveform acquisition parameters
        if sparsing == 0:
            sparsing = 1
        self.waveform_sparsing = sparsing
        self.waveform_points = requested_points
        self.waveform_first_point = 0

        # Calculate how many points are to be expected
        sample_points = self.acquisition_sample_size(self.waveform_source)
        if requested_points > 0:
            expected_points = min(requested_points, int(sample_points / sparsing))
        else:
            expected_points = int(sample_points / sparsing)

        # If the number of points is big enough, split the data in small chunks and read it one
        # chunk at a time. For less than a certain amount of points we do not bother splitting them.
        chunk_bytes = 20000
        chunk_points = chunk_bytes - self._header_size - self._footer_size
        iterations = -(expected_points // -chunk_points)
        i = 0
        data = []
        while i < iterations:
            # number of points already read
            read_points = i * chunk_points
            # number of points still to read
            remaining_points = expected_points - read_points
            # number of points requested in a single chunk
            requested_points = chunk_points if remaining_points > chunk_points else remaining_points
            self.waveform_points = requested_points
            # number of bytes requested in a single chunk
            requested_bytes = requested_points + self._header_size + self._footer_size
            # read the next chunk starting from this points
            first_point = read_points * sparsing
            self.waveform_first_point = first_point
            # read chunk of points
            values = self._digitize(src=self.waveform_source, block=block, num_bytes=requested_bytes)
            # perform many sanity checks on the received data
            self._header_footer_sanity_checks(values,block=block)
            self._npoints_sanity_checks(values)
            # append the points without the header and footer
            data.append(values[self._header_size:-self._footer_size])
            i += 1
        data = np.concatenate(data)
        preamble = self.waveform_preamble
        
        # Determine sampling rate (horizontal interval) from waveform descriptor
        preamble['sampling_rate'] = 1/self.waveform_descriptor.horiz_ival

        return data, preamble
    

    def _process_data(self, ydata, preamble):
        """Apply scale and offset to the data points acquired from the scope.
        - Y axis : the scale is given by descriptor.vgain and the offset -descriptor.vos. the
        offset is not applied for the MATH source.
        - X axis : the scale is given by descriptor.horiz_ival*i + descriptor.horiz_os for i = 0,1,...,N. 
        :return: tuple of (numpy array of Y points, numpy array of X points, waveform preamble) """

        data_points = np.array(unpack('<'+'b'*len(ydata),ydata))
        data_points = data_points*self.waveform_descriptor.vgain
        if preamble['source'] != 'MATH':
            data_points = data_points - self.waveform_descriptor.vos 
        time_points = np.arange(len(data_points))*self.waveform_descriptor.horiz_ival*preamble['sparsing'] + self.waveform_descriptor.horiz_os
        return data_points, time_points, preamble


    #################
    # Download data #
    #################

    hardcopy_setup_current = Instrument.measurement(
        "HCSU?",
        """Get current hardcopy config.""",
        get_process_list=_results_list_to_dict,
    )

    def hardcopy_setup(self, **kwargs):
        """Specify hardcopy settings.

        Connect a printer or define how to save to file. Set any or all
        of the following parameters.

        :param device: {BMP, JPEG, PNG, TIFF}
        :param format: {PORTRAIT, LANDSCAPE}
        :param background: {Std, Print, BW}
        :param destination: {PRINTER, CLIPBOARD, EMAIL, FILE, REMOTE}
        :param area: {GRIDAREAONLY, DSOWINDOW, FULLSCREEN}
        :param directory: Any legal DOS path, for FILE mode only
        :param filename: Filename string, no extension, for FILE mode only
        :param printername: Valid printer name, for PRINTER mode only
        :param portname: {GPIB, NET}
        """
        keys = {
            "device": "DEV",
            "format": "FORMAT",
            "background": "BCKG",
            "destination": "DEST",
            "area": "AREA",
            "directory": "DIR",
            "filename": "FILE",
            "printername": "PRINTER",
            "portname": "PORT",
        }

        arg_strs = [keys[key] + "," + value for key, value in kwargs.items()]

        self.write("HCSU " + ",".join(arg_strs))

    def download_image(self, **kwargs):
        """Get a BMP image of oscilloscope screen in bytearray of specified file format.

        The hardcopy destination is set to "REMOTE" by default.

        :param \\**kwargs: Keyword arguments for :meth:`hardcopy_setup`
        """
        kwargs.setdefault("destination", "REMOTE")
        self.hardcopy_setup(**kwargs)
        return super().download_image()
    
    def download_waveform(self, source, requested_points=None, sparsing=None, block='DAT1'):
        """Get data points from the specified source of the oscilloscope.

        The returned objects are two np.ndarray of data and time points and a dict with the
        waveform preamble, that contains metadata about the waveform.

        :param source: measurement source. It can be "C1", "C2", "C3", "C4", "MATH".
        :param requested_points: number of points to acquire. If None the number of points
               requested in the previous call will be assumed, i.e. the value of the number of
               points stored in the oscilloscope memory. If 0 the maximum number of points will
               be returned.
        :param sparsing: interval between data points. For example if sparsing = 4, only one
               point every 4 points is read. If 0 or None the sparsing of the previous call is
               assumed, i.e. the value of the sparsing stored in the oscilloscope memory.
        :param block: waveform data block. "DESC","TEXT","TIME","DAT1","DAT2","ALL"
        :return: data_ndarray, time_ndarray, waveform_preamble_dict: see waveform_preamble
                 property for dict format.
        """
        # Sanitize the input arguments
        if not sparsing:
            sparsing = self.waveform_sparsing
        elif sparsing == 0:
            sparsing = 1
        if requested_points is None:
            requested_points = self.waveform_points
        self.waveform_source = sanitize_source(source)
        # Acquire the Y data and the preamble
        ydata, preamble = self._acquire_data(requested_points, sparsing, block=block)
        # Update the preamble with info about actually acquired data
        preamble["transmitted_points"] = len(ydata)
        preamble["requested_points"] = requested_points
        preamble["sparsing"] = sparsing
        preamble["first_point"] = 0
        # Scale the Y-data and create the X-data
        return self._process_data(ydata, preamble)

    ###############
    # Acquisition #
    ###############
    def acquisition_sample_size(self,source = None):
        """Get acquisition sample size. For MAUI oscilloscopes this seems to be the memory size."""
        return self.memory_size
