#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

from pymeasure.instruments.instrument import ActiveDSOInstrument


class WaveRunner606Zi(ActiveDSOInstrument):
    """ Represents the WaveRunner 606Zi Oscilloscope
    and provides a high-level for interacting with the instrument
    """
    def __init__(self, address):
        super(WaveRunner606Zi, self).__init__(
            address=address,
            name="LeCroy WaveRunner 606Zi Oscilloscope",
        )

        self.measurement = WaveRunner606Zi.Measurement(self)

    def disconnect(self):
        return super(WaveRunner606Zi, self).disconnect()

    def recall_setup_from_file(self, filename):
        """ Command to setup osci from file based on filename
        cmd = "RCPN DISK, HDD, FILE," + filename.
        """
        return self.write("%s" % ("RCPN DISK, HDD, FILE," + filename))

        # TODO: must be new implemented self.port.tty.StoreHardcopyToFile('TIFF', '', filename)
        # WaveRunner606Zi.print_screen_tif= Instrument.control()

    id = ActiveDSOInstrument.id

    query_options = ActiveDSOInstrument.measurement(
        "*OPT?", "" "Query the scope options. """
    )

    timespan = ActiveDSOInstrument.control(
        "TIME_DIV?", "TIME_DIV %g",
        """ A floating point property that controls the timespan of the horizontal axis
        This property can be set.
        """
    )

    def get_measurement_Px(self, num):
        """Use special access to Lecroy with VBS
        get the value of the ma"""
        value = self.adapter.ask("VBS? 'return=app.Measure.P%d.Out.Result.Value' " % num)
        return value

    def save_c1_trc(self):
        """Save C1 Analog Waveform in TRC format"""
        self.adapter.write("VBS 'app.SaveRecall.Waveform.SaveSource = \"C1\"' ")
        self.adapter.write("VBS 'app.SaveRecall.Waveform.DoSave' ")
        """Wait until all traces are saved"""
        self.adapter.write("*OPC?")
        txt =  self.adapter.read()

    def save_c2_trc(self):
        """Save C2 Analog Waveform in TRC format"""
        self.adapter.write("VBS 'app.SaveRecall.Waveform.SaveSource = \"C2\"' ")
        self.adapter.write("VBS 'app.SaveRecall.Waveform.DoSave' ")
        """Wait until all traces are saved"""
        self.adapter.write("*OPC?")
        txt =  self.adapter.read()

    def save_c3_trc(self):
        """Save C3 Analog Waveform in TRC format"""
        self.adapter.write("VBS 'app.SaveRecall.Waveform.SaveSource = \"C3\"' ")
        self.adapter.write("VBS 'app.SaveRecall.Waveform.DoSave' ")
        """Wait until all traces are saved"""
        self.adapter.write("*OPC?")
        txt =  self.adapter.read()        

    def save_c4_trc(self):
        """Save C4 Analog Waveform in TRC format"""
        self.adapter.write("VBS 'app.SaveRecall.Waveform.SaveSource = \"C4\"' ")
        self.adapter.write("VBS 'app.SaveRecall.Waveform.DoSave' ")
        """Wait until all traces are saved"""
        self.adapter.write("*OPC?")
        txt =  self.adapter.read()
    
    def save_all_displayed_trc(self):
        """Save "All Displayed" Analog Waveforms"""
        self.adapter.write("VBS 'app.SaveRecall.Waveform.SaveSource = \"AllDisplayed\"' ")
        self.adapter.write("VBS 'app.SaveRecall.Waveform.DoSave' ")
        """Wait until all traces are saved"""
        self.adapter.write("*OPC?")
        txt =  self.adapter.read()

    def save_screen_to_file(self, filename):
        """this function print the screen to HDD in Oscillo
        I met some problem with StoreHardcopyToFile due to oscillo crash"""
        #self.adapter.connection.StoreHardcopyToFile("TIFF", "", "D:\\HardCopy\\TIFFImage.tif")
        self.adapter.write("VBS 'app.Hardcopy.EnableCounterSuffix = \"False\"' ")
        self.adapter.write("VBS 'app.Hardcopy.PreferredFilename = \"%s.png\"' " % filename)
        self.adapter.write("VBS? 'app.Hardcopy.Print' ")

    class Measurement(object):

        SOURCE_VALUES = ['C1', 'C2', 'C3', 'C4', 'F1', 'F2', 'F3', 'F4']

        def __init__(self, parent):
            self.parent = parent

        def amplitude(self, source):
            """Get signal amplitude"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? AMPL'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def area(self, source):
            """Get signal integral"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? area'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def cyclesnumber(self, source):
            """Get the number of signal cycle"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? CYCL'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def falltime90to10(self, source):
            """Get fall time from 90% to 10% """
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? FALL'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def frequency(self, source):
            """Get signal frequency"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? FREQ'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def max(self, source):
            """Get signal maximimum"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? MAX'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def mean(self, source):
            """Get signal mean"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? MEAN'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def min(self, source):
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? MIN'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def peak2peak(self, source):
            """Get signal peak to peak value"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? PKPK'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def period(self, source):
            """Get signal period"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? PER'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def risetime10to90(self, source):
            """Get rise time from 10% to 90% """
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? RISE'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def rms(self, source):
            """Get signal RMS value"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? RMS'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def std_dev(self, source):
            """Get signal stansard deviation"""
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? SDEV'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def top(self, source):
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? TOP'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def width(self, source):
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? WID'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def width_neg(self, source):
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? widthn'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

        def duty(self, source):
            if source in WaveRunner606Zi.Measurement.SOURCE_VALUES:
                value = self.parent.ask("%s" % (source + ':PAVA? DUTY'))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                    self.parent, source))
            return float(value.split(',')[1])

