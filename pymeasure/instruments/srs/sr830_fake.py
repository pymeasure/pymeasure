from time import perf_counter

import numpy as np
from scipy.signal import butter, lti, freqresp

from pymeasure.instruments.validators import truncated_discrete_set
from pymeasure.adapters import FakeScpiAdapter

from pymeasure.instruments.srs import SR830

class FakeSR830DUT:
    """
    A simulated device-under-test for a FakeSr830Adapter. Simulates a
    second-order bandpass (or lowpass or highpass) response with some
    oscillatory measurement transients from the LIA lowpass filter, in order to
    allow testing of settling detection logic.

    Note that this simulated device runs in real time, i.e., it will check
    actual elapsed time to generate data. It is not possible to manually set
    timesteps; it is suggested instead that frequency and tau values are
    scaled appropriately for testing purposes.

    :param fmin: lower 3dB cutoff. None to disable.
    :param fmax: upper 3dB cutoff. None to disable.
    """

    def __init__(self, fmin=None, fmax=2000):
        self.fmin = fmin
        self.fmax = fmax
        self.lti = self.make_lti()

        self.t0 = 0
        self._f = None
        self.meas_r = None
        self.meas_p = None
        self.last_r = None
        self.last_p = None

    def make_lti(self):
        order = 2
        if self.fmin is not None and self.fmax is not None:
            b, a = butter(order, [2*np.pi*self.fmin, 2*np.pi*self.fmax], btype='band',
                analog=True)
        elif self.fmin is None and self.fmax is not None:
            b, a = butter(order, 2*np.pi*self.fmax, btype='lowpass', analog=True)
        elif self.fmax is None and self.fmin is not None:
            b, a = butter(order, 2*np.pi*self.fmin, btype='highpass', analog=True)
        else:
            b, a = [1], [1]
        return lti(b, a)

    def configure(self, frequency, tau):
        """
        Configure the current test conditions.
        
        :param float frequency: Frequency (Hz) of the input signal to the DUT.
        :param float tau: Time constant (s) of the LIA filter.
        """
        # validate
        if frequency < 0.001 or frequency > 102000:
            raise ValueError("Frequency {:.3f} Hz out of range".format(frequency))

        # store parameters
        self.t0 = perf_counter()
        self._f = frequency
        self.tau = truncated_discrete_set(tau, SR830.TIME_CONSTANTS)
        self.last_r = self.meas_r if self.meas_r is not None else 0
        self.last_p = self.meas_p if self.meas_r is not None else 0

        # calculate response target
        _, meas = freqresp(self.lti, w=[2 * np.pi * self._f])
        self.meas_r = np.absolute(meas[0])
        self.meas_p = np.angle(meas[0], deg=True)


    def r(self):
        """ Return the current magnitude measurement (in VRMS). """
        t = perf_counter() - self.t0
        return (self.meas_r - self.last_r) \
                * (1 - np.exp(-4.5*t/(10*self.tau)) * np.cos(t/self.tau)) \
                + self.last_r

    def theta(self):
        """ Return the current phase measurement (in degrees). """
        t = perf_counter() - self.t0
        return (self.meas_p - self.last_p) \
                * (1 - np.exp(-4.5*t/(10*self.tau)) * np.cos(t/self.tau + np.pi/2)) \
                + self.last_r


class FakeSR830Adapter(FakeScpiAdapter):
    """
    An SR830 simulator, for testing a PyMeasure measurement routine independent
    of physical test bench equipment and set-up.

    Implements SR830 default settings on reset, as well as simulating the
    lowpass filter transient for X, Y, magnitude and phase via the ``OUTP``
    command.

    Does not currently support other measurement commands.

    :param dut: A FakeSR830DUT object. Only needs to be constructed; this
        Adapter will configure it as needed.
    """
    def __init__(self, dut, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dut = dut
        self.set_value('*IDN', 'Stanford_Research_Systems,SR830,s/n99999,ver9.999')
        self.set_handler('OUTP', self.outp_handler)
        self.set_handler('*RST', self.reset_handler)
        self.set_handler('FREQ', self.freq_handler)
        self.set_handler('OFLT', self.tau_handler)

        self._freq = 1000.0
        self._tau = 0.1


    def reset_handler(self, args=tuple(), query=False):
        if query:
            raise ValueError("*RST not queryable")

        # REFERENCE / PHASE
        self.set_value('PHAS', 0.0)
        self.set_value('FMOD', 1)
        self.set_value('HARM', 1)
        self.set_value('SLVL', 1.000)
        self.freq_handler(args=(1000.0), query=False)
        self.set_value('RSLP', 0)

        # INPUT / FILTERS
        self.set_value('ISRC', 0)
        self.set_value('IGND', 0)
        self.set_value('ICPL', 0)
        self.set_value('ILIN', 0)

        # GAIN / TC
        self.set_value('SENS', 26)
        self.set_value('RMOD', 2)
        self.tau_handler(args=(8), query=False)
        self.set_value('OFSL', 1)
        self.set_value('SYNC', 0)

        # DISPLAY
        # CH1 display = X (not supported in simulator)
        # CH2 display = Y (not supported in simulator)
        # Ratio = None (not supported in PyMeasure)
        # Reference = Frequency (?)

        # OUTPUT / OFFSET
        # Offsets not supported in PyMeasure

        # AUX OUTPUTS
        # Not supported in PyMeasure

        # SETUP
        # Adapter-level stuff, shouldn't matter

        # DATA STORAGE
        # Not supported in simulator


    def outp_handler(self, args=tuple(), query=False):
        if not query:
            raise ValueError('Query-only command')

        measid = args[0]

        if measid == 1:
            r, theta = self._dut.r(), self._dut.theta()
            return r * np.cos(theta*np.pi/180)
        elif measid == 2:
            r, theta = self._dut.r(), self._dut.theta()
            return r * np.sin(theta*np.pi/180)
        elif measid == 3:
            return self._dut.r()
        elif measid == 4:
            return self._dut.theta()


    def freq_handler(self, args=tuple(), query=False):
        if query:
            return self._freq
        else:
            self._freq = float(args[0])
            self._dut.configure(self._freq, self._tau)


    def tau_handler(self, args=tuple(), query=False):
        if query:
            return SR830.TIME_CONSTANTS.index(self._tau)
        else:
            self._tau = SR830.TIME_CONSTANTS[args[0]]
            self._dut.configure(self._freq, self._tau)

