#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    import zmq
    from msgpack_numpy import dumps
except ImportError:
    log.warning("ZMQ and MsgPack are required for TCP communication")

from multiprocessing import Process, Queue, current_process
from ..experiment.listeners import Listener, Daemon, Server
from pymeasure.adapters.visa import VISAAdapter
from pymeasure.adapters import FakeAdapter
import inspect, types, os

import numpy as np

class InstrumentBase(object):
    """ Base class for Instruments, independent of the particular Adapter used
    to connect for communication
    """
    def __init__(self, adapter, name, includeSCPI=True, port=None, **kwargs):
        if port is None:
            try:
                if isinstance(adapter, (int, str)):
                    adapter = VISAAdapter(adapter, **kwargs)
            except ImportError:
                raise Exception("Invalid Adapter provided for Instrument since "
                                "PyVISA is not present")
        else:
            adapter = FakeAdapter()

        self.instrument_name = name
        self.SCPI = includeSCPI
        self.adapter = adapter
        class Object(object):
            pass
        self.get = Object()

        # TODO: Determine case basis for the addition of these methods
        if includeSCPI:
            # Basic SCPI commands
            #self.add_measurement("id",       "*IDN?")
            self.add_measurement("status",   "*STB?")
            self.add_measurement("complete", "*OPC?")

        self._params = [a[0] for a in inspect.getmembers(type(self), lambda a: type(a)==property)]
        self._functions = [f[0] for f in inspect.getmembers(type(self), lambda a:type(a) == types.FunctionType) if (not(f[0].startswith('_')))]

        self.isShutdown = False
        log.info("Initializing %s." % self.instrument_name)

    @property
    def id(self):
        if self.SCPI:
            return self.adapter.ask("*IDN?").strip()
        else:
            return "Warning: Property not implemented."

    # Wrapper functions for the Adapter object
    def ask(self, command):
        return self.adapter.ask(command)

    def write(self, command):
        self.adapter.write(command)

    def read(self):
        return self.adapter.read()

    def values(self, command, separator = ','):
        return self.adapter.values(command, separator = separator)

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        return self.adapter.binary_values(command, header_bytes, dtype)

    def add_property(self, name, initial_value=0.0):
        """This adds simple setter and getter properties called "name"
        for the internal variable that will be called _name
        """
        # Define the property first
        setattr(self, "_"+name, initial_value)

        def fget(self):
            return getattr(self, "_"+name)

        def fset(self, value):
            setattr(self, "_"+name, value)

        # Add the property attribute
        setattr(self.__class__, name, property(fget, fset))
        # Set convenience functions, that we may pass by reference if necessary
        setattr(self.__class__, 'set_'+name, fset)
        setattr(self.__class__, 'get_'+name, fget)

    def add_control(self, name, get_string, set_string,
                    check_errors_on_set=False,
                    check_errors_on_get=False,
                    docs=None
                    ):
        """This adds a property to the class based on the supplied
        SCPI commands. The presumption is that this parameter may
        be set and read from the instrument."""

        def fget(self):
            vals = self.values(get_string)
            if check_errors_on_get:
                self.check_errors()
            if len(vals) == 1:
                return vals[0]
            else:
                return vals

        def fset(self, value):
            self.write(set_string % value)
            if check_errors_on_set:
                self.check_errors()

        # Add the specified document string to the getter
        fget.__doc__ = docs

        # Add the property attribute
        setattr(self.__class__, name, property(fget, fset))
        setattr(self.get, name, lambda: fget(self))


    def add_measurement(self, name, get_string, checkErrorsOnGet=False, docs=None):
        """This adds a property to the class based on the supplied
        SCPI commands. The presumption is that this is a measurement
        quantity that may only be read from the instrument, not set.
        """

        def fget(self):
            vals = self.values(get_string)
            if len(vals) == 1:
                return vals[0]
            else:
                return vals

        # Add the specified document string to the getter
        fget.__doc__ = docs

        # Add the property attribute
        setattr(self.__class__, name, property(fget))
        setattr(self.get, name, lambda: fget(self))

    # TODO: Determine case basis for the addition of this method
    def clear(self):
        self.write("*CLS")

    # TODO: Determine case basis for the addition of this method
    def reset(self):
        self.write("*RST")

    def shutdown(self):
        """Bring the instrument to a safe and stable state"""
        self.isShutdown = True
        log.info("Shutting down %s" % self.name)

    def check_errors(self):
        """Return any accumulated errors. Must be reimplemented by subclasses.
        """
        pass

class Commands(object):
    """ Commands evaluates commands for an instrument and returns the result
    """
    def __init__(self, instrument, response_queue):
        self.instrument = instrument
        self.command_queue = Queue()
        self.response_queue = response_queue

    def eval(self, command):
        try:
            if '=' in cmd:
                cmd = cmd.replace(' =','=')
                cmd = cmd.replace('= ','=')
                param, value = re.split('=',cmd)
                if param in self.instrument._params:
                    setattr(self.instrument, param, eval(value))
                else:
                    logging.warning('Instrument %s does not have attribute %s.' %(instrument._name, param))
                response = 'True'
            if '(' in cmd:
                response = eval('self.instrument.' + cmd)
            else:
                response = str(getattr(self.instrument, cmd))
            return response
        except Exception as e:
            logging.warning('Command \'%s\' not recognized: %s' %(cmd, e))
            return None

class InstrumentDaemon(InstrumentBase, Daemon):
    """ InstrumentDaemon runs a loop in a thread and executes instrument commands as received
    """
    instances = []
    def __init__(self, adapter, name, includeSCPI=True, queue=None, **kwargs):
        self.commands = Commands(self, queue)

        self.instrument_name = name
        self.running = True

        log.info("Initializing %s InstrumentDaemon." % self.instrument_name)

        InstrumentBase.__init__(self, adapter=adapter, name=name, includeSCPI=True)
        Daemon.__init__(self)
        InstrumentDaemon.instances.append(self)
        self.start()

def get_instrument_server(port = None, scribe_queue=None, log_level=logging.INFO):
    """ Get instance of InstrumentServer for specified port"""
    if port in InstrumentServer.instances.keys():
        return InstrumentServer.instances[port]
    else:
        return InstrumentServer(port, scribe_queue, log_level)

class InstrumentServer(Server):
    """ InstrumentServer manages an adapter and runs InstrumentDaemon threads for each
    instrument connected to the interface."""
    instances = {}
    def __init__(self, port = 5001, log_queue=None, log_level=logging.INFO):
        self.port = port
        self.queue = Queue()
        super(InstrumentServer, self).__init__(port, log_queue, log_level)
        InstrumentServer.instances[port] = self
        self.start()

    def create_instrument(self, instrument_class, adapter):
        module_name = instrument_class.__module__
        class_name = instrument_class.__name__
        data = ['create_instrument', [module_name, class_name, adapter]]
        self.queue.put(data)

    def create_daemon(self, module_name, class_name, adapter):
        mod = __import__(module_name, fromlist=[class_name])
        instrument_class = getattr(mod, class_name)
        daemon = instrument_class(adapter, queue=self.queue)
        self.daemons.append(daemon)

class Instrument(InstrumentBase if current_process().name == 'MainProcess' else InstrumentDaemon):
    def __init__(self, adapter, name, includeSCPI=True, queue=None, port=None, **kwargs):
        if port is None:
            super(Instrument, self).__init__(adapter, name, includeSCPI=True, queue=queue, **kwargs)