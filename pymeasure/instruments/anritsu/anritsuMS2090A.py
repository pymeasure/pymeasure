#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    truncated_range,
    double_validation_value_and_freq
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AnritsuMS2090A(Instrument):
    """Anritsu MS2090A Handheld Spectrum Analyzer."""

    def __init__(self, adapter, **kwargs):
        """Constructor."""
        self.analysis_mode = None
        super().__init__(
            adapter, name="Anritsu MS2090A Handheld Spectrum Analyzer", **kwargs)

    #############
    #  Mappings #
    #############

    ONOFF = ["ON", "OFF"]
    ONOFF_MAPPING = {True: 'ON', False: 'OFF', 1: 'ON', 0: 'OFF', 'ON': 'ON', 'OFF': 'OFF'}
    OFFFIRSTREPEAT = ['OFF', 'FIRSt', 'REPeat']
    SPAMODES = ["SPECtrum", "NRADio", "RTSA", "LTE", "EMFMeter", "PANalyzer"]
    UNITSFREQ = ['Hz', 'kHz', 'MHz', 'GHz']
    UNITSFREQ_MAP = []

    ####################################
    #              GPS                 #
    ####################################

    gps_full = Instrument.measurement(
        "FETCh:GPS:FULL?",
        '''
        Returns the timestamp, latitude, longitude, altitude, and satellite count of the device.
        '''
    )

    gps_all = Instrument.measurement(
        "FETCh:GPS:ALL?",
        '''
        Returns the fix timestamp, latitude, longitude, altitude and information on the sat used.
        '''
    )

    gps = Instrument.measurement(
        ":FETCh:GPS?",
        '''
        Returns the timestamp, latitude, and longitude of the device.
        '''
    )

    gps_last = Instrument.measurement(
        ":FETCh:GPS:LAST?",
        '''
        Returns the timestamp, latitude, longitude, and altitude of the last fixed GPS result.
        '''
    )

    external_current = Instrument.measurement(
        "BIAS:EXT:CURR?",
        '''
        This command queries the actual bias current in A
        '''
    )

    ####################################
    # Spectrum Parameters - Wavelength #
    ####################################

    frequency_center = Instrument.control(
        "FREQuency:CENTer?", "FREQuency:CENTer %s",
        "Sets the center frequency in Hz",
        validator=double_validation_value_and_freq,
        values=[[-99999999995, 299999999995], UNITSFREQ]
    )

    frequency_offset = Instrument.control(
        "FREQuency:OFFSet?", "FREQuency:OFFSet %s",
        "Sets the frequency offset in Hz",
        validator=double_validation_value_and_freq,
        values=[[-10000000000, 10000000000], UNITSFREQ],
    )

    frequency_span = Instrument.control(
        "FREQuency:SPAN?", "FREQuency:SPAN %s",
        "Sets the frequency span in Hz",
        validator=double_validation_value_and_freq,
        values=[[10, 400000000000], UNITSFREQ],
    )

    frequency_span_full = Instrument.setting(
        "FREQuency:SPAN:FULL",
        "Sets the frequency span to full span"
    )

    frequency_span_last = Instrument.setting(
        "FREQuency:SPAN:LAST",
        "Sets the frequency span to the previous span value."
    )

    frequency_start = Instrument.control(
        "FREQuency:STARt?", "FREQuency:STARt %s",
        "Sets the start frequency in Hz",
        validator=double_validation_value_and_freq,
        values=[[-100000000000, 299999999990], UNITSFREQ],
    )

    frequency_step = Instrument.control(
        ":FREQuency:STEP?", ":FREQuency:STEP %s",
        "Set or query the step size to gradually increase or decrease frequency values in Hz",
        validator=double_validation_value_and_freq,
        values=[[0.1, 1000000000], UNITSFREQ],
    )

    frequency_stop = Instrument.control(
        "FREQuency:STOP?", "FREQuency:STOP %s",
        "Sets the start frequency in Hz",
        validator=double_validation_value_and_freq,
        values=[[-99999999990, 300000000000], UNITSFREQ],
    )

    abort = Instrument.setting(
        "ABOR",
        '''
        Abort measure
        '''
    )

    fet_power = Instrument.measurement(
        "FET:CHP:CHP?",
        '''
        Returns the most recent channel power measurement.
        '''
    )

    fet_density = Instrument.measurement(
        "FET:CHP:DEN?",
        '''
        Returns the most recent channel density measurement
        '''
    )

    fet_pbch_constellation = Instrument.measurement(
        "FET:CONS:PBCH",
        '''
        Get the latest Physical Broadcast Channel constellation hitmap
        '''
    )

    fet_pdsch_constellation = Instrument.measurement(
        "FET:CONS:PDSC?",
        '''
        Get the latest Physical Downlink Shared Channel constellation
        '''
    )

    fet_control = Instrument.measurement(
        "FET:CONT?",
        '''
        Returns the Control Channel measurement in json format.
        '''
    )

    fet_eirpower = Instrument.measurement(
        "FET:EIRP?",
        '''
        Returns the current EIRP, Max EIRP, Horizontal EIRP, Vertical and Sum EIRP results in dBm.
        '''
    )

    fet_eirpower_data = Instrument.measurement(
        "FET:EIRP:DAT?",
        '''
        This command returns the current EIRP measurement result in dBm.
        '''
    )

    fet_eirpower_max = Instrument.measurement(
        "FET:EIRP:MAX?",
        '''
        This command returns the Max EIRP measurement result in dBm.
        '''
    )

    fet_emf = Instrument.measurement(
        "FET:EMF?",
        '''
        Return the current EMF measurement data. JSON format.
        '''
    )

    fet_emf_meter = Instrument.measurement(
        "FET:EMF:MET?",
        '''
        Return the live EMF measurement data. JSON format.
        '''
    )

    fet_emf_meter_sample = Instrument.measurement(
        "FET:EMF:MET:SAM%g?",
        '''
        Return the EMF measurement data for a specified sample number. JSON format.
        ''',
        validator=truncated_range,
        values=[1, 16],
    )

    fet_interference_power = Instrument.measurement(
        "FET:INT:POW?",
        '''
        Fetch Interference Finder Integrated Power.
        '''
    )

    fet_mimo_antenas = Instrument.measurement(
        "FET:MIMO:ANT?",
        '''
        Returns the sync power measurement in json format.
        '''
    )

    fet_ocupied_bw = Instrument.measurement(
        "FET:OBW%g?",
        '''
        Returns the different set of measurement information depending on the suffix.
        ''',
        validator=truncated_range,
        values=[1, 2]
    )

    fet_ota_mapping = Instrument.measurement(
        "FET:OTA:MAPP?",
        '''
        Returns the most recent Coverage Mapping measurement result.
        '''
    )

    fet_pan = Instrument.measurement(
        "FET:PAN?",
        '''
        Return the current Pulse Analyzer measurement data. JSON format
        '''
    )

    fet_pci = Instrument.measurement(
        "FET:PCI?",
        '''
        Returns PCI measurements
        '''
    )

    fet_pdsch = Instrument.measurement(
        "FET:PDSC?",
        '''
        Returns the Data Channel Measurements in JSON format.
        '''
    )

    fet_peak = Instrument.measurement(
        "FET:PEAK?",
        '''
        Returns a pair of peak amplitude in current sweep.
        '''
    )

    fet_rrm = Instrument.measurement(
        "FET:RRM?",
        '''
        Returns the Radio Resource Management in JSON format.
        '''
    )

    fet_scan = Instrument.measurement(
        "FET:SCAN?",
        '''
        Returns the cell scanner measurements in JSON format
        '''
    )

    fet_semask = Instrument.measurement(
        "FET:SEM?",
        '''
        This command returns the current Spectral Emission Mask measurement result.
        '''
    )

    fet_ssb = Instrument.measurement(
        "FET:SSB?",
        '''
        Returns the SSB measurement
        '''
    )

    fet_sync_evm = Instrument.measurement(
        "FET:SYNC:EVM?",
        '''
        Returns the Sync EVM measurement in JSON format.
        '''
    )

    fet_sync_power = Instrument.measurement(
        "FET:SYNC:POW?",
        '''
        Returns the sync power measurements in JSON format
        '''
    )

    fet_tae = Instrument.measurement(
        "FET:TAE?",
        '''
        Returns the Time Alignment Error in JSON format.
        '''
    )

    init_continuous = Instrument.control(
        "INIT:CONT?", "INIT:CONT %g",
        "Specified whether the sweep/measurement is triggered continuously",
        values=ONOFF,
        map_values=True
    )

    init_sweep = Instrument.setting(
        "INIT",
        '''
        Initiates a sweep/measurement.
        '''
    )

    init_sweep_all = Instrument.setting(
        "INIT:ALL",
        '''
        Initiates sweep until all active traces reach its average count
        '''
    )

    init_spa_self = Instrument.measurement(
        "INIT:SPA:SELF?",
        docs='''
        Perform a self-test and return the results.
        '''
    )

    inst_active_state = Instrument.control(
        "INST:ACT:STAT?", "INST:ACT:STAT %g",
        docs='''
        The "set" state indicates that the instrument is used by someone.
        ''',
        values=ONOFF,
        map_values=True
    )

    meas_acpower = Instrument.measurement(
        "MEAS:ACP?",
        '''
        Sets the active measurement to adjacent channel power ratio, sets the default
        measurement parameters, triggers a new measurement and returns the main channel
        power, lower adjacent, upper adjacent, lower alternate and upper alternate channel
        power results.
        '''
    )

    meas_power_all = Instrument.measurement(
        "MEAS:CHP?",
        '''
        Sets the active measurement to channel power, sets the default measurement
        parameters, triggers a new measurement and returns the channel power and channel
        power density results. It is a combination of the commands :CONFigure:CHPower;
        :READ:CHPower?
        '''
    )

    meas_power = Instrument.measurement(
        "MEASure:CHPower:CHPower?",
        '''
        Sets the active measurement to channel power, sets the default measurement
        parameters, triggers a new measurement and returns channel power as the result. It is a
        combination of the commands :CONFigure:CHPower; :READ:CHPower:CHPower?
        '''
    )

    meas_density = Instrument.measurement(
        "MEASure:CHPower:DENSity?",
        '''
        Sets the active measurement to channel power, sets the default measurement
        parameters, triggers a new measurement and returns channel power density as the
        result. It is a combination of the commands :CONFigure:CHPower;
        :READ:CHPower:DENSity?
        '''
    )

    meas_emf_meter_clear_all = Instrument.setting(
        "MEASure:EMF:METer:CLEar:ALL",
        '''
        Clear the EMF measurement data of all samples.
        Sampling state will be turned off if it was on.
        '''
    )

    meas_emf_meter_clear_sample = Instrument.setting(
        "MEASure:EMF:METer:CLEar:SAMPle%g",
        '''
        Clear the EMF measurement data for a specified sample number.
        Sampling state will be turned off if the specified sample is currently active.
        ''',
        validator=truncated_range,
        values=[1, 16],
    )

    meas_emf_meter_sample = Instrument.control(
        "MEASure:EMF:METer:SAMPle:STATe?", "MEASure:EMF:METer:SAMPle:STATe%g",
        docs='''
        Start or Stop applying the measurement results to the currently selected sample
        ''',
        values=ONOFF,
        map_values=True,
    )

    meas_int_power = Instrument.measurement(
        "MEASure:INTerference:POWer?",
        '''
        Sets the active measurement to interference finder, sets the default measurement
        parameters, triggers a new measurement and returns integrated power as the result. It
        is a combination of the commands :CONFigure:INTerference;
        :READ:INTerference:POWer?
        '''
    )

    meas_iq_capture = Instrument.setting(
        "MEASure:IQ:CAPTure",
        '''
        This set command is used to start the IQ capture measurement.
        '''
    )

    meas_iq_capture_fail = Instrument.control(
        "MEASure:IQ:CAPTure:FAIL?", "MEASure:IQ:CAPTure:FAIL %g",
        '''
        Sets or queries whether the instrument will automatically save an IQ capture when
        losing sync
        ''',
        values=OFFFIRSTREPEAT
    )

    meas_ota_mapp = Instrument.measurement(
        "MEASure:OTA:MAPPing?",
        '''
        Sets the active measurement to OTA Coverage Mapping, sets the default measurement
        parameters, triggers a new measurement, and returns the measured values.
        '''
    )

    meas_ota_run = Instrument.control(
        "MEASure:OTA:MAPPing:RUN?", "MEASure:OTA:MAPPing:RUN %g",
        '''
        Turn on/off OTA Coverage Mapping Data Collection. The instrument must be in
        Coverage Mapping measurement for the command to be effective
        ''',
        values=ONOFF,
        map_values=True
    )

    view_sense_modes = Instrument.measurement(
        "MODE:CATalog?",
        '''
        Returns a list of available modes for the Spa application. The response is a
        comma-separated list of mode names. See command [:SENSe]:MODE for the mode name
        specification.
        '''
    )

    sense_mode = Instrument.control(
        "MODE?", ":MODE %g",
        '''
        Set the operational mode of the Spa app.
        ''',
        values=SPAMODES,
    )

    preamp = Instrument.control(
        "POWer:RF:GAIN:STATe?", "POWer:RF:GAIN:STATe %g",
        '''
        Sets the state of the preamp. Note that this may cause a change in the reference level
        and/or attenuation.
        ''',
        values=ONOFF,
        validator=strict_discrete_set
    )
