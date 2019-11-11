#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

import typing
import logging
import re
from abc import ABC, abstractmethod

import numpy as np

from pymeasure.instruments.instrument import Instrument
from pymeasure.adapters import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ChannelHAL(object):
    __slots__ = ("hal",)

    def __init__(self, hal):
        self.hal = hal


class IChannel(ABC):
    __slots__ = ("id", "hal")
    HAL_CLASS = ChannelHAL

    def __init__(self, hal, id):
        self.id = id
        self.hal = self.__class__.HAL_CLASS(hal)

    @property
    @abstractmethod
    def unit(self):
        raise NotImplementedError()

    @unit.setter
    @abstractmethod
    def unit(self, v):
        raise NotImplementedError()

    @property
    @abstractmethod
    def scale(self):
        raise NotImplementedError()

    @scale.setter
    @abstractmethod
    def scale(self, v):
        raise NotImplementedError()

    @property
    @abstractmethod
    def offset(self):
        raise NotImplementedError()

    @offset.setter
    @abstractmethod
    def offset(self, v):
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def total_points(self):
        raise NotImplementedError()

    @abstractmethod
    def get_samples_per_channel_sample(self, chn):
        raise NotImplementedError()

    @abstractmethod
    def set_samples_per_channel_sample(self, chn, v):
        raise NotImplementedError()

    def __repr__(self):
        return self.id + "<" + ", ".join(k + "=" + repr(getattr(self, k)) for k in self.__slots__) + ">"


class VisibleChannel(IChannel):
    __slots__ = ()

    @property
    @abstractmethod
    def visible(self):
        raise NotImplementedError()

    @visible.setter
    @abstractmethod
    def visible(self, v):
        raise NotImplementedError()


class AcquisitionChannelMixin(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def memory_size(self):
        return NotImplementedError()

    @memory_size.setter
    @abstractmethod
    def memory_size(self, v):
        raise NotImplementedError()


class IWaveformAcquisitor:
    __slots__ = ("hal", "channels")

    def __init__(self, hal, channels=None):
        self.hal = hal
        self.channels = channels


class OscilloscopeHAL(ABC):
    __slots__ = ("inst", "acquisitorClass")

    def __init__(self, inst, acquisitorClass):
        self.inst = inst
        self.acquisitorClass = acquisitorClass

    @property
    @abstractmethod
    def mode(self):
        raise NotImplementedError()

    @mode.setter
    @abstractmethod
    def mode(self, v):
        raise NotImplementedError()
    
    @property
    def locked(self):
        pass

    @locked.setter
    def locked(self, v):
        return False

    @abstractmethod
    def trigger(self):
        raise NotImplementedError()

    @abstractmethod
    def getChannelsList(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def get_display_picture(self, format):
        raise NotImplementedError()

    def beep():
        raise NotImplementedError()


class VendorHALDispatcher:
    def __call__(self, ins: Instrument):
        raise NotImplementedError()


class ModelDictHALDispatcher(VendorHALDispatcher):
    dispatch_by = "model"

    def __init__(self, dic, default=None):
        self.dic = dic
        self.default = default

    def __call__(self, ins: Instrument):
        model = ins.id_dict[self.__class__.dispatch_by].lower()
        if model in self.dic:
            return self.dic[model]
        else:
            if self.default is not None:
                return self.default
            raise NotImplementedError()


class VendorDictHALDispatcher(ModelDictHALDispatcher):
    dispatch_by = "vendor"

from .rigol import RigolHALDispatcher

registered_hals = VendorDictHALDispatcher({
    "rigol technologies": RigolHALDispatcher
})


class Oscilloscope(object):
    __slots__ = ("hal", "channels", "channelsMapping")

    def decodeFormats(self):
        for words, letter in self.hal.getSupportedFormats().items():
            yield (words, (letter, struct.calcsize(letter)))

    def selectWaveformFormat(self):
        return max(self.supportedFormats.items(), key=lambda f: f[1][1])

    def getAcquisitor(self, channels):
        if channels is None:
            channels = self.channels
        return self.hal.acquisitorClass(self.hal, channels)
    
    def __getitem__(self, k):
        return self.channelsMapping[k]
    

    def __init__(self, instrument: typing.Union[int, str, Adapter, Instrument], includeSCPI=True, **kwargs):
        ins = instrument
        if isinstance(ins, (int, str, Adapter)):
            ins = Instrument(ins, None, **kwargs)

        vendorHALDispatcher = registered_hals(ins)
        modelHALClass = vendorHALDispatcher(ins)
        self.hal = modelHALClass(ins)

        print("self.hal", self.hal)
        self.channels, self.channelsMapping = self.hal.getChannelsList()
        print("self.channels, self.channelsMapping", self.channels, self.channelsMapping)
        self.hal.locked = False

        #ins.id
        #ins.values(self, command, **kwargs)
        #ins.binary_values(self, command, **kwargs)
        #ins.binary_values(self, command, **kwargs)
        #ins.clear
        #ins.reset
        #ins.shutdown
        #ins.check_errors

        #instrument.__class__.control
        """Returns a property for the class based on the supplied
        commands. This property may be set and read from the
        instrument.

        :param get_command: A string command that asks for the value
        :param set_command: A string command that writes the value
        :param docs: A docstring that will be included in the documentation
        :param validator: A function that takes both a value and a group of valid values
                          and returns a valid value, while it otherwise raises an exception
        :param values: A list, tuple, range, or dictionary of valid values, that can be used
                       as to map values if :code:`map_values` is True.
        :param map_values: A boolean flag that determines if the values should be
                          interpreted as a map
        :param get_process: A function that take a value and allows processing
                            before value mapping, returning the processed value
        :param set_process: A function that takes a value and allows processing
                            before value mapping, returning the processed value
        :param check_set_errors: Toggles checking errors after setting
        :param check_get_errors: Toggles checking errors after getting
        """

        ins.__class__.measurement
        """ Returns a property for the class based on the supplied
        commands. This is a measurement quantity that may only be
        read from the instrument, not set.

        :param get_command: A string command that asks for the value
        :param docs: A docstring that will be included in the documentation
        :param values: A list, tuple, range, or dictionary of valid values, that can be used
                       as to map values if :code:`map_values` is True.
        :param map_values: A boolean flag that determines if the values should be
                          interpreted as a map
        :param get_process: A function that take a value and allows processing
                            before value mapping, returning the processed value
        :param command_process: A function that take a command and allows processing
                            before executing the command, for both getting and setting
        :param check_get_errors: Toggles checking errors after getting
        """

        ins.__class__.setting
        """ Returns a property for the class based on the supplied
        commands. This is a measurement quantity that may only be
        read from the instrument, not set.

        :param get_command: A string command that asks for the value
        :param docs: A docstring that will be included in the documentation
        :param values: A list, tuple, range, or dictionary of valid values, that can be used
                       as to map values if :code:`map_values` is True.
        :param map_values: A boolean flag that determines if the values should be
                          interpreted as a map
        :param get_process: A function that take a value and allows processing
                            before value mapping, returning the processed value
        :param command_process: A function that take a command and allows processing
                            before executing the command, for both getting and setting
        :param check_get_errors: Toggles checking errors after getting
        """
