# Classes for Communicating over GPIB Bus
#
# Authors: Colin Jermain
# Copyright: 2012 Cornell University
#

from zope.interface import implementer
from automate import interfaces
from automate.instruments import Instrument

class GPIBInstrument(Instrument):
    """ Base class for a GPIB Instrument that typically uses a
    GPIBAdapter object (or other IConnection implementing object)
    to communicate to a specific address on the bus    
    """
    
    def __init__(self, adapter, address):
        self.address = address
        super(GPIBInstrument, self).__init__(adapter)
        
    def write(self, command):
        """ Writes to the connection and ensures the correct GPIB address 
        is referenced during the transaction
        """
        self.connection.write(command, self.address)
        
    def identify(self):
        """ Returns the response of the instrument to an identification request
        """
        return self.ask("*IDN?")
        
    def reset(self):
        """ Sends a command to reset the instrument """
        self.write("*RST")

        
@implementer(interfaces.IConnection)
class PrologixAdapter(object):
    """ Encapsulates the additional commands necessary
    to communicate over a Prologix GPIB-USB Adapter and
    implements the IConnection interface    
    """

    def __init__(self, port, timeout=0.5):
        import serial
        self.connection = serial.Serial(port, 9600, timeout=timeout)
        self.setDefaults()

    def setDefaults(self):
        self.write("++auto 0") # Turn off auto read-after-write
        self.write("++eoi 1") # Append end-of-line to commands
        self.write("++eos 2") # Append line-feed to commands
        
    def open(self):
        if not self.isOpen():
            self.connection.open()
              
    def close(self):
        if self.isOpen():
            self.connection.close()
        
    def isOpen(self):
        return self.connection.isOpen()
                
    def flush(self):
        self.connection.flush()

    def write(self, command, address=None):
        if address is not None:
            self.connection.write("++addr %d\n" % address)
        self.connection.write(command + "\n")
        
    def read(self):
        """ Reads until timeout, returning string """
        return "\n".join(self.readlines())
        
    def readline(self):
        """ Read till end-of-line, returning string """ 
        self.write("++read eoi")
        return self.connection.readline()
        
    def readlines(self):
        """ Reads until timeout, returns list """
        self.write("++read")
        return self.connection.readlines()        

""" PyVISA is required to use the VISAAdapter class,
but PyVISA is not required to use the automate package
"""
try:
    import visa
 
    @implementer(interfaces.IConnection)
    class VISAAdapter(object):
        """ Encapsulates the additional commands necessary
        to communicate over a PyVISA instrument class and
        implements the IConnection interface
        """

        def __init__(self, instrument):
            assert isinstance(instrument, visa.Instrument)
            self.instrument = instrument
            
        def open(self):
            if not self.isOpen():
                self.connection.open()
                  
        def close(self):
            if self.isOpen():
                self.connection.close()
            
        def isOpen(self):
            return self.connection.isOpen()
                    
        def write(self, command, address=None):
            self.instrument.write(command)
            
        def read(self):
            """ Reads until timeout, returning string """
            return self.instrument.read()
            
        def readline(self):
            """ Read till end-of-line, returning string """ 
            self.write("++read eoi")
            return self.connection.readline()
            
        def readlines(self):
            """ Reads until timeout, returns list """
            self.write("++read")
            return self.connection.readlines()
except ImportError:
    pass
