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

# Requires 'instrumental' package: https://github.com/mabuchilab/Instrumental

from instrumental.drivers.daq import ni
from pymeasure.instruments import Instrument

def get_dict_attr(obj,attr):
    for obj in [obj]+obj.__class__.mro():
        if attr in obj.__dict__:
            return obj.__dict__[attr]
    raise AttributeError

class NIDAQ(Instrument):
	'''
	Instrument driver for NIDAQ card.
	'''
	def __init__(self, name='Dev1', *args, **kwargs):
		self._daq  = ni.NIDAQ(name)
		super(NIDAQ, self).__init__(
			None,
			"NIDAQ",
			includeSCPI = False,
			**kwargs)
		for chan in self._daq.get_AI_channels():
			self.add_property(chan)
		for chan in self._daq.get_AO_channels():
			self.add_property(chan, set=True)

	def add_property(self, chan, set=False):
		if set:
			fset = lambda self, value: self.set_chan(chan, value)
			fget = lambda self: getattr(self, '_%s' %chan)
			setattr(self, '_%s' %chan, None)
			setattr(self.__class__,chan,property(fset=fset, fget=fget))
		else:
			fget = lambda self: self.get_chan(chan)
			setattr(self.__class__,chan,property(fget=fget))
		setattr(self.get, chan, lambda: getattr(self, chan))

	def get_chan(self, chan):
		return getattr(self._daq,chan).read().magnitude
	
	def set_chan(self, chan, value):
		setattr(self, '_%s' %chan, value)
		getattr(self._daq,chan).write('%sV' %value)
