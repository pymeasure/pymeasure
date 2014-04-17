from zope.interface import Interface, implementer

class IConnection(Interface):
    """
    Object used to represent a connection over which an instrument
    can be communicated through    
    """
    
    def open():
        """
        Open the connection to the instrument
        """
        
    def close():
        """
        Close the established connection with the instrument
        """
        
    def isOpen():
        """
        Returns True if the instrument has an open connection
        """

    def flush():
        """
        Flushes the read buffer contents
        """
        
    def write():
        """
        Writes a string command through the connection
        """
        
    def read():
        """
        Reads the instrument response until the end of line and returns
        the full response as a string
        """
        
    def readline():
        """
        Reads a line from the instrument through the connection and returns
        a string of the line
        """
        
    def readlines():
        """
        Reads all lines from the instrument through the connection and returns
        a list of the lines
        """

class IInstrument(Interface):
    """
    Object used to represent an instrument to and from which commands are
    issued through a connection implementing IConnection
    """
    
    def connect():
        """
        Open the connection to the instrument if it is not already open
        """
        
    def disconnect():
        """
        Close the connection to the instrument if it is open
        """
        
    def isConnected():
        """
        Returns True if the instrument has an open connection
        """
