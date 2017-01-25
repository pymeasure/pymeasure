#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
#
# Python USBTMC driver, lifted from python-usbtmc.
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
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import sys
import time
import struct
import re
import usb.core
import usb.util
from .adapter import Adapter

# constants
USBTMC_bInterfaceClass    = 0xFE
USBTMC_bInterfaceSubClass = 3
USBTMC_bInterfaceProtocol = 0
USB488_bInterfaceProtocol = 1

USBTMC_MSGID_DEV_DEP_MSG_OUT            = 1
USBTMC_MSGID_REQUEST_DEV_DEP_MSG_IN     = 2
USBTMC_MSGID_DEV_DEP_MSG_IN             = 2
USBTMC_MSGID_VENDOR_SPECIFIC_OUT        = 126
USBTMC_MSGID_REQUEST_VENDOR_SPECIFIC_IN = 127
USBTMC_MSGID_VENDOR_SPECIFIC_IN         = 127
USB488_MSGID_TRIGGER                    = 128

USBTMC_STATUS_SUCCESS                  = 0x01
USBTMC_STATUS_PENDING                  = 0x02
USBTMC_STATUS_FAILED                   = 0x80
USBTMC_STATUS_TRANSFER_NOT_IN_PROGRESS = 0x81
USBTMC_STATUS_SPLIT_NOT_IN_PROGRESS    = 0x82
USBTMC_STATUS_SPLIT_IN_PROGRESS        = 0x83
USB488_STATUS_INTERRUPT_IN_BUSY        = 0x20

USBTMC_REQUEST_INITIATE_ABORT_BULK_OUT     = 1
USBTMC_REQUEST_CHECK_ABORT_BULK_OUT_STATUS = 2
USBTMC_REQUEST_INITIATE_ABORT_BULK_IN      = 3
USBTMC_REQUEST_CHECK_ABORT_BULK_IN_STATUS  = 4
USBTMC_REQUEST_INITIATE_CLEAR              = 5
USBTMC_REQUEST_CHECK_CLEAR_STATUS          = 6
USBTMC_REQUEST_GET_CAPABILITIES            = 7
USBTMC_REQUEST_INDICATOR_PULSE             = 64

USB488_READ_STATUS_BYTE = 128
USB488_REN_CONTROL      = 160
USB488_GOTO_LOCAL       = 161
USB488_LOCAL_LOCKOUT    = 162

USBTMC_HEADER_SIZE = 12

RIGOL_QUIRK_PIDS = [0x04ce, 0x0588]


def parse_visa_resource_string(resource_string):
    """Parse a VISA resource string."""
    # valid resource strings:
    # USB::1234::5678::INSTR
    # USB::1234::5678::SERIAL::INSTR
    # USB0::0x1234::0x5678::INSTR
    # USB0::0x1234::0x5678::SERIAL::INSTR
    m = re.match('^(?P<prefix>(?P<type>USB)\d*)(::(?P<arg1>[^\s:]+))'
                 '(::(?P<arg2>[^\s:]+(\[.+\])?))(::(?P<arg3>[^\s:]+))?'
                 '(::(?P<suffix>INSTR))$', resource_string, re.I)

    if m is not None:
        return dict(
            type=m.group('type').upper(),
            prefix=m.group('prefix'),
            arg1=m.group('arg1'),
            arg2=m.group('arg2'),
            arg3=m.group('arg3'),
            suffix=m.group('suffix')
        )

#
# Exceptions
#


class USBTMCError(Exception):
    """Custom USBTMC Error class."""

    em = {0: "No error"}

    def __init__(self, err=None, note=None):
        """Constructor.

        :param err: The error code or message string
        :param note: An extra note to print
        """
        self.err = err
        self.note = note
        self.msg = ''

        if err is None:
            self.msg = note
        else:
            if type(err) is int:
                if err in self.em:
                    self.msg = "%d: %s" % (err, self.em[err])
                else:
                    self.msg = "%d: Unknown error" % err
            else:
                self.msg = err
            if note is not None:
                self.msg = "%s [%s]" % (self.msg, note)

    def __str__(self):
        """String representation method override."""
        return self.msg


def list_devices():
    """List all connected USBTMC devices."""
    def is_usbtmc_device(dev):
        for cfg in dev:
            d = usb.util.find_descriptor(cfg, bInterfaceClass=USBTMC_bInterfaceClass,
                                         bInterfaceSubClass=USBTMC_bInterfaceSubClass)
            is_advantest = dev.idVendor == 0x1334
            return d is not None or is_advantest

    return list(usb.core.find(find_all=True, custom_match=is_usbtmc_device))


def find_device(idVendor=None, idProduct=None, iSerial=None):
    """Find a connected USBTMC instrument."""
    devs = list_devices()

    if len(devs) == 0:
        return None

    for dev in devs:
        if dev.idVendor != idVendor or dev.idProduct != idProduct:
            continue

        if iSerial is None:
            return dev
        else:
            s = ''

            # try reading serial number
            try:
                s = dev.serial_number
            except:
                pass

            if iSerial == s:
                return dev

    return None


class USBTMCAdapter(Adapter):
    """USBTMC instrument interface client.

    The USBTMC protocol is used in some modern controllers.  Connection is
    performed via a USB device.  Not a serial connection.
    """

    def __init__(self, *args, **kwargs):
        """Create new USBTMC instrument object.

        Takes a variable number of arguments, allowing for a variety of
        instantiation mechanisms.  this allows for connection of any number of devices on the system USB bus.

        :param *args: Variable positional arguments
        :param **kwargs: Variable key word arguments

        :raises ValueError: Thrown when input arguments cannot be parsed
        :raises USBTMCError: Thrown when configured device is not available
        ie:

        # Any single string argument is processed as a VISA resource string
        adapter = USBTMC('VISA::08')

        # Alternatively, specify the device by a combination of its idVendor,
        # idProduct, and/or, idSerial property.
        # These can be provided as positional arguments or as key word arguments.
        adapter = USBTMC(idVendor, idProduct)
        adapter = USBTMC(idVendor=1234, idProduct=4321)
        adapter = USBTMC(idVendor, idProduct, idSerial)

        :raises UsbTmcError
        """
        self.idVendor = 0
        self.idProduct = 0
        self.iSerial = None
        self.device = None
        self.cfg = None
        self.iface = None
        self.term_char = None
        self.advantest_quirk = False
        self.advantest_locked = False
        self.rigol_quirk = False
        self.rigol_quirk_ieee_block = False

        self.bcdUSBTMC = 0
        self.support_pulse = False
        self.support_talk_only = False
        self.support_listen_only = False
        self.support_term_char = False

        self.bcdUSB488 = 0
        self.support_USB4882 = False
        self.support_remote_local = False
        self.support_trigger = False
        self.support_scpi = False
        self.support_SR = False
        self.support_RL = False
        self.support_DT = False

        self.max_transfer_size = 1024 * 1024

        self.timeout = 5.0

        self.bulk_in_ep = None
        self.bulk_out_ep = None
        self.interrupt_in_ep = None

        self.last_btag = 0
        self.last_rstb_btag = 0

        self.connected = False
        self.reattach = []
        self.old_cfg = None

        self.encoding = 'utf-8'
        resource = None

        # process arguments
        if len(args) == 1:
            if type(args[0]) == str:
                resource = args[0]
            else:
                self.device = args[0]
        if len(args) >= 2:
            self.idVendor = args[0]
            self.idProduct = args[1]
        if len(args) >= 3:
            self.iSerial = args[2]

        for op in kwargs:
            val = kwargs[op]
            if op == 'idVendor':
                self.idVendor = val
            elif op == 'idProduct':
                self.idProduct = val
            elif op == 'iSerial':
                self.iSerial = val
            elif op == 'device':
                self.device = val
            elif op == 'dev':
                self.device = val
            elif op == 'term_char':
                self.term_char = val
            elif op == 'resource':
                resource = val
            elif op == 'encoding':
                self.encoding = encoding
        if resource is not None:
            res = parse_visa_resource_string(resource)

            if res is None:
                raise ValueError("Invalid resource string")

            if res['arg1'] is None and res['arg2'] is None:
                raise ValueError("Invalid resource string")

            self.idVendor = int(res['arg1'], 0)
            self.idProduct = int(res['arg2'], 0)
            self.iSerial = res['arg3']

        # find device
        if self.device is None:
            if self.idVendor is None or self.idProduct is None:
                raise USBTMCError("No device specified", 'init')
            else:
                self.device = find_device(self.idVendor, self.idProduct, self.iSerial)
                if self.device is None:
                    raise USBTMCError("Device not found", 'init')

    def __del__(self):
        """Delete method override."""
        if self.connected:
            self.close()

    def open(self):
        """Open the configured device if not already connected."""
        if self.connected:
            return

        # initialize device

        # find first USBTMC interface
        for cfg in self.device:
            for iface in cfg:
                if (self.device.idVendor == 0x1334) or \
                   (iface.bInterfaceClass == USBTMC_bInterfaceClass and
                   iface.bInterfaceSubClass == USBTMC_bInterfaceSubClass):
                    self.cfg = cfg
                    self.iface = iface
                    break
                else:
                    continue
            break

        if self.iface is None:
            raise USBTMCError("Not a USBTMC device", 'init')

        try:
            self.old_cfg = self.device.get_active_configuration()
        except usb.core.USBError:
            # ignore exception if configuration is not set
            pass

        if self.old_cfg is not None and self.old_cfg.bConfigurationValue == self.cfg.bConfigurationValue:
            # already set to correct configuration

            # release kernel driver on USBTMC interface
            self._release_kernel_driver(self.iface.bInterfaceNumber)
        else:
            # wrong configuration or configuration not set

            # release all kernel drivers
            if self.old_cfg is not None:
                for iface in self.old_cfg:
                    self._release_kernel_driver(iface.bInterfaceNumber)

            # set proper configuration
            self.device.set_configuration(self.cfg)

        # claim interface
        usb.util.claim_interface(self.device, self.iface)

        # don't need to set altsetting - USBTMC devices have 1 altsetting as per the spec

        # find endpoints
        for ep in self.iface:
            ep_dir = usb.util.endpoint_direction(ep.bEndpointAddress)
            ep_type = usb.util.endpoint_type(ep.bmAttributes)

            if (ep_type == usb.util.ENDPOINT_TYPE_BULK):
                if (ep_dir == usb.util.ENDPOINT_IN):
                    self.bulk_in_ep = ep
                elif (ep_dir == usb.util.ENDPOINT_OUT):
                    self.bulk_out_ep = ep
            elif (ep_type == usb.util.ENDPOINT_TYPE_INTR):
                if (ep_dir == usb.util.ENDPOINT_IN):
                    self.interrupt_in_ep = ep

        if self.bulk_in_ep is None or self.bulk_out_ep is None:
            raise USBTMCError("Invalid endpoint configuration", 'init')

        # set quirk flags if necessary
        if self.device.idVendor == 0x1334:
            # Advantest/ADCMT devices have a very odd USBTMC implementation
            # which requires max 63 byte reads and never signals EOI on read
            self.max_transfer_size = 63
            self.advantest_quirk = True

        if self.device.idVendor == 0x1ab1 and self.device.idProduct in RIGOL_QUIRK_PIDS:
            self.rigol_quirk = True

            if self.device.idProduct == 0x04ce:
                self.rigol_quirk_ieee_block = True

        self.connected = True

        self.clear()

        self.get_capabilities()

    def close(self):
        """Close the configured device."""
        if not self.connected:
            return

        usb.util.dispose_resources(self.device)

        try:
            # reset configuration
            if self.cfg.bConfigurationValue != self.old_cfg.bConfigurationValue:
                self.device.set_configuration(self.old_cfg)

            # try to reattach kernel driver
            for iface in self.reattach:
                try:
                    self.device.attach_kernel_driver(iface)
                except:
                    pass
        except:
            pass

        self.reattach = []

        self.connected = False

    def is_usb488(self):
        """Return a boolean whether connected device supports the USB488 protocol."""
        return self.iface.bInterfaceProtocol == USB488_bInterfaceProtocol

    def get_capabilities(self):
        """Get the capabilities of the currently connected device.

        :raises USBTMCError: Thrown when device does not properly return capabilities.
        """
        if not self.connected:
            self.open()

        b = self.device.ctrl_transfer(
            usb.util.build_request_type(
                usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_INTERFACE),
            USBTMC_REQUEST_GET_CAPABILITIES,
            0x0000,
            self.iface.index,
            0x0018,
            timeout=int(self.timeout * 1000))

        if (b[0] == USBTMC_STATUS_SUCCESS):
            self.bcdUSBTMC = (b[3] << 8) + b[2]
            self.support_pulse = b[4] & 4 != 0
            self.support_talk_only = b[4] & 2 != 0
            self.support_listen_only = b[4] & 1 != 0
            self.support_term_char = b[5] & 1 != 0

            if self.is_usb488():
                self.bcdUSB488 = (b[13] << 8) + b[12]
                self.support_USB4882 = b[4] & 4 != 0
                self.support_remote_local = b[4] & 2 != 0
                self.support_trigger = b[4] & 1 != 0
                self.support_scpi = b[4] & 8 != 0
                self.support_SR = b[4] & 4 != 0
                self.support_RL = b[4] & 2 != 0
                self.support_DT = b[4] & 1 != 0
        else:
            raise USBTMCError("Get capabilities failed", 'get_capabilities')

    def pulse(self):
        """Send a pulse indicator request.

        This should blink a light
        for 500-1000ms and then turn off again. (Only if supported)
        """
        if not self.connected:
            self.open()

        if self.support_pulse:
            b = self.device.ctrl_transfer(
                usb.util.build_request_type(
                    usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS,
                    usb.util.CTRL_RECIPIENT_INTERFACE),
                USBTMC_REQUEST_INDICATOR_PULSE,
                0x0000,
                self.iface.index,
                0x0001,
                timeout=int(self.timeout * 1000))
            if (b[0] != USBTMC_STATUS_SUCCESS):
                raise USBTMCError("Pulse failed", 'pulse')

    # message header management
    def pack_bulk_out_header(self, msgid):
        self.last_btag = btag = (self.last_btag % 255) + 1
        return struct.pack('BBBx', msgid, btag, ~btag & 0xFF)

    def pack_dev_dep_msg_out_header(self, transfer_size, eom=True):
        hdr = self.pack_bulk_out_header(USBTMC_MSGID_DEV_DEP_MSG_OUT)
        return hdr + struct.pack("<LBxxx", transfer_size, eom)

    def pack_dev_dep_msg_in_header(self, transfer_size, term_char=None):
        hdr = self.pack_bulk_out_header(USBTMC_MSGID_DEV_DEP_MSG_IN)
        transfer_attributes = 0
        if term_char is None:
            term_char = 0
        else:
            transfer_attributes = 2
            term_char = self.term_char
        return hdr + struct.pack("<LBBxx", transfer_size, transfer_attributes, term_char)

    def pack_vendor_specific_out_header(self, transfer_size):
        hdr = self.pack_bulk_out_header(USBTMC_MSGID_VENDOR_SPECIFIC_OUT)
        return hdr + struct.pack("<Lxxxx", transfer_size)

    def pack_vendor_specific_in_header(self, transfer_size):
        hdr = self.pack_bulk_out_header(USBTMC_MSGID_VENDOR_SPECIFIC_IN)
        return hdr + struct.pack("<Lxxxx", transfer_size)

    def pack_usb488_trigger(self):
        hdr = self.pack_bulk_out_header(USB488_MSGID_TRIGGER)
        return hdr + b'\x00' * 8

    def unpack_bulk_in_header(self, data):
        msgid, btag, btaginverse = struct.unpack_from('BBBx', data)
        return (msgid, btag, btaginverse)

    def unpack_dev_dep_resp_header(self, data):
        msgid, btag, btaginverse = self.unpack_bulk_in_header(data)
        transfer_size, transfer_attributes = struct.unpack_from('<LBxxx', data, 4)
        data = data[USBTMC_HEADER_SIZE:transfer_size + USBTMC_HEADER_SIZE]
        return (msgid, btag, btaginverse, transfer_size, transfer_attributes, data)

    def write_raw(self, data):
        """Write binary data to instrument."""
        if not self.connected:
            self.open()

        eom = False

        num = len(data)

        offset = 0

        try:
            while num > 0:
                if num <= self.max_transfer_size:
                    eom = True

                block = data[offset:offset + self.max_transfer_size]
                size = len(block)

                req = self.pack_dev_dep_msg_out_header(size, eom) + block + b'\0' * ((4 - (size % 4)) % 4)
                self.bulk_out_ep.write(req, timeout=int(self.timeout * 1000))

                offset += size
                num -= size
        except usb.core.USBError:
            exc = sys.exc_info()[1]
            if exc.errno == 110:
                # timeout, abort transfer
                self._abort_bulk_out()
            raise

    def read_raw(self, num=-1):
        """Read binary data from instrument."""
        if not self.connected:
            self.open()

        read_len = self.max_transfer_size
        if 0 < num < read_len:
            read_len = num

        eom = False

        term_char = None

        if self.term_char is not None:
            term_char = self.term_char

        read_data = b''

        try:
            while not eom:
                if not self.rigol_quirk or read_data == b'':

                    # if the rigol sees this again, it will restart the transfer
                    # so only send it the first time

                    req = self.pack_dev_dep_msg_in_header(read_len, term_char)
                    self.bulk_out_ep.write(req, timeout=int(self.timeout * 1000))

                resp = self.bulk_in_ep.read(
                    read_len + USBTMC_HEADER_SIZE + 3, timeout=int(self.timeout * 1000))

                if sys.version_info >= (3, 2):
                    resp = resp.tobytes()
                else:
                    resp = resp.tostring()

                if self.rigol_quirk and read_data:
                    # do nothing, the packet has no header if it isn't the first
                    pass
                else:
                    (msgid, btag, btaginverse, transfer_size,
                     transfer_attributes, data) = self.unpack_dev_dep_resp_header(resp)

                if self.rigol_quirk:
                    # rigol devices only send the header in the first packet,
                    # and they lie about whether the transaction is complete
                    if read_data:
                        read_data += resp
                    else:
                        if self.rigol_quirk_ieee_block and data.startswith(b"#"):

                            # ieee block incoming, the transfer_size usbtmc
                            # header is lying about the transaction size
                            l = int(chr(data[1]))
                            n = int(data[2:l + 2])

                            transfer_size = n + (l + 2)  # account for ieee header

                        read_data += data

                    if len(read_data) >= transfer_size:
                        read_data = read_data[:transfer_size]  # as per usbtmc spec section 3.2 note 2
                        eom = True
                    else:
                        eom = False
                else:
                    eom = transfer_attributes & 1
                    read_data += data

                # Advantest devices never signal EOI and may only send one
                # read packet
                if self.advantest_quirk:
                    break

                if num > 0:
                    num = num - len(data)
                    if num <= 0:
                        break
                    if num < read_len:
                        read_len = num
        except usb.core.USBError:
            exc = sys.exc_info()[1]
            if exc.errno == 110:
                # timeout, abort transfer
                self._abort_bulk_in()
            raise

        return read_data

    def ask_raw(self, data, num=-1):
        """Write then read binary data."""
        # Advantest/ADCMT hardware won't respond to a command unless it's in Local Lockout mode
        was_locked = self.advantest_locked
        try:
            if self.advantest_quirk and not was_locked:
                self.lock()
            self.write_raw(data)
            return self.read_raw(num)
        finally:
            if self.advantest_quirk and not was_locked:
                self.unlock()

    def write(self, message):
        """Write a string or list of strings to the instrument."""
        if type(message) is tuple or type(message) is list:
            # recursive call for a list of commands
            for message_i in message:
                self.write(message_i, self.encoding)
            return

        self.write_raw(str(message).encode(self.encoding))

    def read(self, num=-1):
        """Read string from instrument."""
        return self.read_raw(num).decode(self.encoding).rstrip('\r\n')

    def ask(self, message, num=-1):
        """Write then read string."""
        if type(message) is tuple or type(message) is list:
            # recursive call for a list of commands
            val = list()
            for message_i in message:
                val.append(self.ask(message_i, num, self.encoding))
            return val

        # Advantest/ADCMT hardware won't respond to a command unless it's in Local Lockout mode
        was_locked = self.advantest_locked
        try:
            if self.advantest_quirk and not was_locked:
                self.lock()
            self.write(message, self.encoding)
            return self.read(num, self.encoding)
        finally:
            if self.advantest_quirk and not was_locked:
                self.unlock()

    def read_stb(self):
        """Read status byte."""
        if not self.connected:
            self.open()

        if self.is_usb488():
            rstb_btag = (self.last_rstb_btag % 128) + 1
            if rstb_btag < 2:
                rstb_btag = 2
            self.last_rstb_btag = rstb_btag

            b = self.device.ctrl_transfer(
                usb.util.build_request_type(
                    usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE),
                USB488_READ_STATUS_BYTE,
                rstb_btag,
                self.iface.index,
                0x0003,
                timeout=int(self.timeout * 1000))
            if (b[0] == USBTMC_STATUS_SUCCESS):
                # check btag
                if rstb_btag != b[1]:
                    raise USBTMCError("Read status byte btag mismatch", 'read_stb')
                if self.interrupt_in_ep is None:
                    # no interrupt channel, value is here
                    return b[2]
                else:
                    # read response from interrupt channel
                    resp = self.interrupt_in_ep.read(2, timeout=int(self.timeout * 1000))
                    if resp[0] != rstb_btag + 128:
                        raise USBTMCError("Read status byte btag mismatch", 'read_stb')
                    else:
                        return resp[1]
            else:
                raise USBTMCError("Read status failed", 'read_stb')
        else:
            return int(self.ask("*STB?"))

    def trigger(self):
        """Send trigger command."""
        if not self.connected:
            self.open()

        if self.support_trigger:
            data = self.pack_usb488_trigger()
            print(repr(data))
            self.bulk_out_ep.write(data, timeout=int(self.timeout * 1000))
        else:
            self.write("*TRG")

    def clear(self):
        """Send clear command."""
        if not self.connected:
            self.open()

        # Send INITIATE_CLEAR
        b = self.device.ctrl_transfer(
            usb.util.build_request_type(
                usb.util.CTRL_IN,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_INTERFACE),
            USBTMC_REQUEST_INITIATE_CLEAR,
            0x0000,
            self.iface.index,
            0x0001,
            timeout=int(self.timeout * 1000))
        if (b[0] == USBTMC_STATUS_SUCCESS):
            # Initiate clear succeeded, wait for completion
            while True:
                # Check status
                b = self.device.ctrl_transfer(
                    usb.util.build_request_type(
                        usb.util.CTRL_IN,
                        usb.util.CTRL_TYPE_CLASS,
                        usb.util.CTRL_RECIPIENT_INTERFACE),
                    USBTMC_REQUEST_CHECK_CLEAR_STATUS,
                    0x0000,
                    self.iface.index,
                    0x0002,
                    timeout=int(self.timeout * 1000))
                if (b[0] == USBTMC_STATUS_PENDING):
                    time.sleep(0.1)
                else:
                    break
            # Clear halt condition
            self.bulk_out_ep.clear_halt()
        else:
            raise USBTMCError("Clear failed", 'clear')

    def _abort_bulk_out(self, btag=None):
        """Abort bulk out."""
        if not self.connected:
            return

        if btag is None:
            btag = self.last_btag

        # Send INITIATE_ABORT_BULK_OUT
        b = self.device.ctrl_transfer(
            usb.util.build_request_type(
                usb.util.CTRL_IN,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_ENDPOINT),
            USBTMC_REQUEST_INITIATE_ABORT_BULK_OUT,
            btag,
            self.bulk_out_ep.bEndpointAddress,
            0x0002,
            timeout=int(self.timeout * 1000))
        if (b[0] == USBTMC_STATUS_SUCCESS):
            # Initiate abort bulk out succeeded, wait for completion
            while True:
                # Check status
                b = self.device.ctrl_transfer(
                    usb.util.build_request_type(
                        usb.util.CTRL_IN,
                        usb.util.CTRL_TYPE_CLASS,
                        usb.util.CTRL_RECIPIENT_ENDPOINT),
                    USBTMC_REQUEST_CHECK_ABORT_BULK_OUT_STATUS,
                    0x0000,
                    self.bulk_out_ep.bEndpointAddress,
                    0x0008,
                    timeout=int(self.timeout * 1000))
                if (b[0] == USBTMC_STATUS_PENDING):
                    time.sleep(0.1)
                else:
                    break
        else:
            # no transfer in progress; nothing to do
            pass

    def _abort_bulk_in(self, btag=None):
        """Abort bulk in."""
        if not self.connected:
            return

        if btag is None:
            btag = self.last_btag

        # Send INITIATE_ABORT_BULK_IN
        b = self.device.ctrl_transfer(
            usb.util.build_request_type(
                usb.util.CTRL_IN,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_ENDPOINT),
            USBTMC_REQUEST_INITIATE_ABORT_BULK_IN,
            btag,
            self.bulk_in_ep.bEndpointAddress,
            0x0002,
            timeout=int(self.timeout * 1000))
        if (b[0] == USBTMC_STATUS_SUCCESS):
            # Initiate abort bulk in succeeded, wait for completion
            while True:
                # Check status
                b = self.device.ctrl_transfer(
                    usb.util.build_request_type(
                        usb.util.CTRL_IN,
                        usb.util.CTRL_TYPE_CLASS,
                        usb.util.CTRL_RECIPIENT_ENDPOINT),
                    USBTMC_REQUEST_CHECK_ABORT_BULK_IN_STATUS,
                    0x0000,
                    self.bulk_in_ep.bEndpointAddress,
                    0x0008,
                    timeout=int(self.timeout * 1000))
                if (b[0] == USBTMC_STATUS_PENDING):
                    time.sleep(0.1)
                else:
                    break
        else:
            # no transfer in progress; nothing to do
            pass

    def remote(self):
        """Send remote command."""
        raise NotImplementedError()

    def local(self):
        """Send local command."""
        raise NotImplementedError()

    def lock(self):
        """Send lock command."""
        if not self.connected:
            self.open()

        if self.advantest_quirk:
            # This Advantest/ADCMT vendor-specific control command enables
            # remote control and must be sent before any commands are exchanged
            # (otherwise READ commands will only retrieve the latest
            # measurement)
            self.advantest_locked = True
            self.device.ctrl_transfer(
                bmRequestType=0xA1, bRequest=0xA0, wValue=0x0001,
                wIndex=0x0000, data_or_wLength=1
            )
        else:
            raise NotImplementedError()

    def unlock(self):
        """Send unlock command."""
        if not self.connected:
            self.open()

        if self.advantest_quirk:
            # This Advantest/ADCMT vendor-specific control command enables
            # remote control and must be sent before any commands are exchanged
            # (otherwise READ commands will only retrieve the latest
            # measurement)
            self.advantest_locked = False
            self.device.ctrl_transfer(
                bmRequestType=0xA1, bRequest=0xA0, wValue=0x0000,
                wIndex=0x0000, data_or_wLength=1
            )
        else:
            raise NotImplementedError()

    def advantest_read_myid(self):
        """Read MyID value from Advantest and ADCMT devices."""
        if not self.connected:
            self.open()

        if self.advantest_quirk:
            # This Advantest/ADCMT vendor-specific control command reads the "MyID" identifier
            try:
                return int(self.device.ctrl_transfer(
                           bmRequestType=0xC1,
                           bRequest=0xF5, wValue=0x0000, wIndex=0x0000,
                           data_or_wLength=1)[0])
            except:
                return None
        else:
            raise NotImplementedError()

    def _release_kernel_driver(self, interface_number):
        if os.name == 'posix':
            if self.device.is_kernel_driver_active(interface_number):
                self.reattach.append(interface_number)
                try:
                    self.device.detach_kernel_driver(interface_number)
                except usb.core.USBError as e:
                    sys.exit(
                        "Could not detach kernel driver from interface({0}): {1}".format(
                            interface_number, str(e)))
