# Instrument Base Class
#
# Authors: Colin Jermain
# Copyright 2013 Cornell University

from automate import interfaces
from zope.interface import implementer

@implementer(interfaces.IInstrument)
class Instrument(object):
    """ Provides the base class for an instrument that uses
    a connection to read and write commands to the instrument.
    The connection is required to implement the IConnector interface.
    """ 
    
    def __init__(self, connection):
        self.connection = interfaces.IConnection(connection)
        
    def connect(self):
        self.connection.open()
        
    def isConnected(self):
        return self.connection.isOpen()
        
    def disconnect(self):
        self.connection.close()
        
    def read(self):
        """ Reads until timeout, returning string """
        return "\n".join(self.connection.readlines())
        
    def readline(self):
        return self.connection.readline()
        
    def readlines(self):
        return self.connection.readlines()
        
    def ask(self, command):
        self.connection.flush()
        self.write(command)
        return self.read()
        
    def write(self, command):
        self.connection.write(command)



class RangeException(Exception): pass

def linearInverse(y, m, b): 
    """ Inverts the fitting parameters to calculate x(y) from y(x)=m*x+b
    """
    return (m**-1)*(float(y) - b)
    
def linearInverseError(y, yError, m, mError, b, bError):
    """ Inverts the fitting parameters to calculate the std(x) from y(x)=m*x+b    
    """
    return ((mError*(b-y)/m**2)**2 + (bError/m)**2 + (yError/m)**2)**0.5

def discreteTruncate(number, discreteSet):
    """ Truncates the number to the closest element in the positive discrete set.
    Returns False if the number is larger than the maximum value or negative.    
    """
    if number < 0:
        return False
    discreteSet.sort()
    for item in discreteSet:
        if number <= item:
            return item
    return False
