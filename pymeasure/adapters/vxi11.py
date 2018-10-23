from pymeasure.adapters import Adapter
import vxi11

class VXI11Adapter(Adapter):
    """ VXI11 Adapter class. Provides a adapter object that
        wraps around the read, write and ask functionality
        of the vxi11 library.

    :param host: string containing the visa connection information.

    """

    def __init__(self, host, **kwargs):

        # Filter valid arguments that can be passed to vxi instrument
        valid_args = ["name", "client_id", "term_char"]
        self.conn_kwargs = {}
        for key in kwargs:
            if key in valid_args:
               self.conn_kwargs[key] = kwargs[key]

        self.connection = vxi11.Instrument(host, **self.conn_kwargs)


    def __repr__(self):
        return "VXI11Adapter connecting to: <{}>".format(self.connection.host)



    def write(self, command):
        """ Wrapper function for the write command using the
        vxi11 interface.

        :param command: string with command the that will be transmitted
                         to the instrument.
        """
        self.connection.write(command)


    def read(self):
        """ Wrapper function for the read command using the
        vx11 interface.

        :return string containing a response from the device.
        """
        return self.connection.read()


    def ask(self, command):
        """ Wrapper function for the ask command using the
        vx11 interface.

        :param command: string with the command that will be transmitted
                        to the instrument.

        :returns string containing a response from the device.
        """
        return self.connection.ask(command)


    def write_raw(self, command):
        """ Wrapper function for the write_raw command using the
        vxi11 interface.

        :param command: binary string with the command that will be
                        transmitted to the instrument
        """
        self.connection.write_raw(command)


    def read_raw(self):
        """ Wrapper function for the read_raw command using the
        vx11 interface.

        :returns binary string containing the response from the device.
        """
        return self.connection.read_raw()


    def ask_raw(self, command):
        """ Wrapper function for the ask_raw command using the
        vx11 interface.

        :param command: binary string with the command that will be
                        transmitted to the instrument

        :returns binary string containing the response from the device.
        """
