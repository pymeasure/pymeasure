#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Generic instrument classes
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from __future__ import print_function
import copy
import numpy as np
import time

class Adapter(object):
    """ Adapts between the Instrument object and the connection, to allow
    flexible use of different connection methods
    """
    
    def write(self, command):
        """ Writes a command """
        raise NameError("Adapter (sub)class has not implemented writing")
        
    def ask(self, command):
        """ Writes the command and returns the read result """
        self.write(command)
        return self.read()
        
    def read(self):
        """ Reads until the buffer is empty and returns the result """
        raise NameError("Adapter (sub)class has not implemented reading")
        
    def values(self, command):
        """ Returns a list of values from the string read """
        raise NameError("Adapter (sub)class has not implemented the values method")
        
    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data """
        raise NameError("Adapter (sub)class has not implemented the binary_values method")

class FakeAdapter(Adapter):
    """Fake adapter for debugging purposes"""
    
    def read(self):
        return "Fake string!"
        
    def write(self, command):
        pass
        
    def values(self, command):
        return [1.0, 2.0, 3.0]
        
    def binary_values(self, command):
        return np.array([2, 3, 7, 8, 1])
        
    def __repr__(self):
        return "<FakeAdapter>"


try:
    import visa
            
    class VISAAdapter(Adapter):
        """ Wrapper class for the VISA library """
        
        def __init__(self, resourceName, **kwargs):
            self.manager = visa.ResourceManager()
            if isinstance(resourceName, (int, long)):
                resourceName = "GPIB0::%d::INSTR" % resourceName            
            if self.version == '1.5':
                safeKeywords = ['resource_name', 'timeout', 'term_chars', 
                                'chunk_size', 'lock', 'delay', 'send_end', 
                                'values_format']
                kwargsCopy = copy.deepcopy(kwargs)
                for key in kwargsCopy:
                    if key not in safeKeywords:
                        kwargs.pop(key)
                self.connection = self.manager.get_instrument(resourceName, **kwargs)
            elif self.version == '1.4':
                self.connection = visa.instrument(resourceName, **kwargs)
        
        @property
        def version(self):
            if hasattr(visa, '__version__'):
                return visa.__version__
            else:
                return '1.4'
            
        def write(self, command):
            self.connection.write(command)
            
        def read(self):
            return self.connection.read()
            
        def ask(self, command):
            return self.connection.ask(command)
        
        def values(self, command):
            return self.connection.ask_for_values(command)
            
        def binary_values(self, command, header_bytes=0, dtype=np.float32):
            self.connection.write(command)
            binary = self.connection.read_raw()
            header, data = binary[:header_bytes], binary[header_bytes:]
            return np.fromstring(data, dtype=dtype)
            
        def wait_for_srq(self, timeout=25, delay=0.1):
            self.connection.wait_for_srq(timeout)
                       
        def __repr__(self):
            return "<VISAAdapter(resource='%s')>" % self.connection.resourceName
except ImportError:
    print("PyVISA library could not be loaded")

try:
    import serial
    
    class SerialAdapter(Adapter):
        """ Wrapper class for the Python Serial package to treat it as an
        adapter
        """
        
        def __init__(self, port, **kwargs):
            self.connection = serial.Serial(port, **kwargs)
        
        def __del__(self):
            self.connection.close()
        
        def write(self, command):
            self.connection.write(command)
            
        def read(self):
            return "\n".join(self.connection.readlines())
            
        def values(self, command):
            result = self.ask(command)
            try:
                return [float(x) for x in result.split(",")]
            except:
                return result.strip()
                
        def binary_values(self, command, header_bytes=0, dtype=np.float32):
            self.connection.write(command)
            binary = self.connection.read()
            header, data = binary[:header_bytes], binary[header_bytes:]
            return np.fromstring(data, dtype=dtype)
            
        def __repr__(self):
            return "<SerialAdapter(port='%s')>" % self.connection.port
            
    class PrologixAdapter(SerialAdapter):
        """ Encapsulates the additional commands necessary
        to communicate over a Prologix GPIB-USB Adapter and
        implements the IConnection interface
        
        To allow user access to the Prologix adapter in Linux, create the file:
        /etc/udev/rules.d/51-prologix.rules, with contents:
        
        SUBSYSTEMS=="usb",ATTRS{idVendor}=="0403",ATTRS{idProduct}=="6001",MODE="0666"
        
        Then reload the udev rules with:
        sudo udevadm control --reload-rules
        sudo udevadm trigger
            
        """
        def __init__(self, port, address=None, **kwargs):
            self.address = address
            if isinstance(port, serial.Serial):
                # A previous adapter is sharing this connection
                self.connection = port
            else:
                # Construct a new connection
                self.connection = serial.Serial(port, 9600, timeout=0.5, **kwargs)
                self.connection.open()
                self.setDefaults()

        def setDefaults(self):
            self.write("++auto 0") # Turn off auto read-after-write
            self.write("++eoi 1") # Append end-of-line to commands
            self.write("++eos 2") # Append line-feed to commands

        def __del__(self):
            if self.connection.isOpen():
                self.connection.close()

        def write(self, command):
            if self.address is not None:
                self.connection.write("++addr %d\n" % self.address)
            self.connection.write(command + "\n")
            
        def read(self):
            """ Reads until timeout """
            self.write("++read")
            return "\n".join(self.connection.readlines())
            
        def gpib(self, gpib_address):
            """ Returns and PrologixAdapter object that references the GPIB 
            address specified, while sharing the Serial connection with other
            calls of this function 
            """
            return PrologixAdapter(self.connection, gpib_address)
            
        def wait_for_srq(self, timeout=25, delay=0.1):
            """ Wait for a SRQ, and leaves the bit high """
            while int(self.ask("++srq")) != 1:
                time.sleep(delay)
            
        def __repr__(self):
            if self.address:
                return "<PrologixAdapter(port='%s',address=%d)>" % (
                        self.port, self.address)
            else:
                return "<PrologixAdapter(port='%s')>" % self.connection.port
            
except ImportError:
    print("PySerial library could not be loaded")


class Instrument(object):
    """ Base class for Instruments, independent of the particular Adapter used
    to connect for communication
    """
    def __init__(self, adapter, name, includeSCPI=True, **kwargs):
        try:
            if isinstance(adapter, (int, long, str)):
                adapter = VISAAdapter(adapter, **kwargs)
        except ImportError:
            raise Exception("Invalid Adapter provided for Instrument since "
                            "PyVISA is not present")
        
        self.name = name
        self.adapter = adapter

        if 'logfunc' in kwargs:
            self.logfunc = kwargs['logfunc']
        else:
            self.logfunc = print

        # TODO: Determine case basis for the addition of these methods
        if includeSCPI:
            # Basic SCPI commands
            self.add_measurement("id",       "*IDN?")
            self.add_measurement("status",   "*STB?")
            self.add_measurement("complete", "*OPC?")

        self.isShutdown = False
        self.log("Initializing <i>%s</i>." % self.name)
        
    # Wrapper functions for the Adapter object
    def ask(self, command): return self.adapter.ask(command)
    def write(self, command): self.adapter.write(command)
    def read(self): return self.adapter.read()
    def values(self, command):
        values = self.adapter.values(command)
        if len(values) == 1:
            return values[0]
        else:
            return values
    def binary_values(self, command, header_bytes=0, dtype=np.float32): 
        return self.adapter.binary_values(command, header_bytes, dtype)

    def add_control(self, name, get_string, set_string, checkErrorsOnSet=False, checkErrorsOnGet=False):
        """This adds a property to the class based on the supplied SCPI commands. The presumption is
        that this parameter may be set and read from the instrument."""
        def fget(self):
            vals = self.values(get_string)
            if checkErrorsOnGet:
                self.check_errors()
            return vals
        def fset(self, value):
            self.write(set_string % value)
            if checkErrorsOnSet:
                self.check_errors()
        # Add the property attribute
        setattr(self.__class__, name, property(fget, fset))
        # Set convenience functions, that we may pass by reference if necessary
        setattr(self.__class__, 'set_'+name, fset)
        setattr(self.__class__, 'get_'+name, fget)

    def add_measurement(self, name, get_string, checkErrorsOnGet=False):
        """This adds a property to the class based on the supplied SCPI commands. The presumption is
        that this is a measurement quantity that may only be read from the instrument, not set."""
        def fget(self):
            return self.values(get_string)
        # Add the property attribute
        setattr(self.__class__, name, property(fget))
        # Set convenience function, that we may pass by reference if necessary
        setattr(self.__class__, 'get_'+name, fget)

    # TODO: Determine case basis for the addition of this method
    def clear(self):
        self.write("*CLS")

    # TODO: Determine case basis for the addition of this method
    def reset(self):
        self.write("*RST")
    
    def shutdown(self):
        """Bring the instrument to a safe and stable state"""
        self.log("Shutting down <i>%s</i>." % self.name)
    
    def check_errors(self):
        """Return any accumulated errors. Must be reimplemented by subclasses."""
        pass

    def log(self, string):
        self.logfunc(string)
        
def discreteTruncate(number, discreteSet):
    """ Truncates the number to the closest element in the positive discrete set.
    Returns False if the number is larger than the maximum value or negative.    
    """
    if number < 0: return False
    discreteSet.sort()
    for item in discreteSet:
        if number <= item: return item
    return False
    
class RangeException(Exception): pass
