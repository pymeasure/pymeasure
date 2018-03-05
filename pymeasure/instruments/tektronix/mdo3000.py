0


class MDO3000(instrument):
    """Represents the Tektronix mixed domain oscilloscopes md3000/md4000 and provides a
    high-level interface for interacting with the instrument.
    Depending on the
    """
    print('nothing here')
    # ToDo: Implement basic OSZI functions to measure and get data
    # ToDo: Make a PyQt GUI that displays both, waveform to send to AFG and measurement DATA




    ##################
    # AFG Properties #
    ##################
    AFG_function = Instrument.control(
        "AFG:FUNCtion?", "AFG:FUNCtion %s",
        """A string property that controls the function of the AFG""",
        validator=strict_discrete_set,
        values={'sine': 'SINE', 'square': 'SQUare', 'pulse': 'PULSe', 'ramp': 'RAMP', 'nois': 'NOISe', 'dc': 'DC',
                'sinc': 'SINC', 'gauss': 'GAUSsian', 'lorentz': 'LORENtz', 'erise': 'ERISe', 'edecay': 'EDECAy',
                'haversine': 'HAVERSINe', 'cardiac': 'CARDIac', 'arbitrary': 'ARBitrary']
    )

    AFG_offset = Instrument.control(
        "AFG:OFFSet?", "AFG:OFFSet %g",
        """A floating point property that represents the AFG offset, in volts. Minimum and Maximum Values depend on the function. NOTE: Load Impedance has to be set before using this function"""
    )

    AFG_loadimpedance = Instrument.control(
        "AFG:OUTPut:LOAd:IMPEDance?", "AFG:OUTPut:LOAd:IMPEDance %s",
        """String property, that sets the AFG load impedance. 'high' or 'fifty' are accepted values.""",
        validator=strict_discrete_set,
        values={'high': 'HIGHZ', 'fifty': 'FIFty'}
    )

    AFG_output = Instrument.control(
        "AFG:OUTPUT:STATE?", "AFG:OUTPUT:STATE %s",
        """String property, that represents the output state ON or OFF""",
        validator=strict_discrete_set,
        values={'ON': 'ON', 'OFF': 'OFF']
    )

    AFG_amplitude = Instrument.control(
        "AFG:AMPLitude?", "AFG:AMPLitude %g",
        """A floating point property that represents the AFG amplitude. Maximum and Minimum Values depend on the selected function. NOTE: Load Impedance has to be set before setting this property""",
    )

    AFG_frequency = Instrument.control(
        "AFG:FREQency?", "AFG:FREQency %g",
        """Floating point property that represents the AFG frequency. Maximum and Minimum Values depend on the selected function. NOTE: Load Impedance has to be set before setting this property"""
    )

    AFG_highlevel = Instrument.control(
        "AFG:HIGHLevel?", "AFG:HIGHLevel %g",
        """Floating point property that represents the AFG low level. Maximum and Minimum Values depend on the selected function. NOTE: Load Impedance has to be set before setting this property"""
    )

    AFG_lowlevel = Instrument.control(
        "AFG:LOWLevel?", "AFG:LOWLevel %g",
        """Floating point property that represents the AFG high level. Maximum and Minimum Values depend on the selected function. NOTE: Load Impedance has to be set before setting this property"""
    )

    AFG_period = Instrument.control(
        "AFG:PERIod?", "AFG:PERIod %g",
        """Floating point property that represents the AFG period. Maximum and Minimum Values depend on the selected function. NOTE: Load Impedance has to be set before setting this property"""
    )

    AFG_phase = Instrument.control(
        "AFG:PHASe?", "AFG:PHASe %g",
        """Floating point property that represents the AFG phase. Maximum and Minimum Values depend on the selected function. NOTE: Load Impedance has to be set before setting this property"""
    )

    AFG_pulsewidth = Instrument.control(
        "AFG:PULse:WIDth?", "AFG:PULse:WIDth %g",
        """Floating Point Property. that represents the AFG pulse width. It has an absolute minimum of 10ns and has a relative range of 10%-90% of the current period setting. Resolution is 0.1ns"""

    )

    AFG_additiveNoise = Instrument.control(
        "AFG:NOISEAdd:PERCent?", "AFG:NOISEAdd:PERCent %g",
        """Floating point property that represents the AFG additive noise level, as a percentage.""",
        validator=truncated_range,
        values=[0, 100]

    )

    AFG_additiveNoiseState = Instrument.control(
        "AFG:NOISEAdd:STATE?", "AFG:NOISEAdd:STATE %s",
        """String property that represents the AFG additive noise state""",
        validator=strict_set,
        values={'ON': 'ON', '1': 'ON', 'OFF': 'OFF', '2': 'OFF'}

    )

    AFG_rampSymmetry = Instrument.control(
        "AFG:RAMP:SYMmetry?", "AFG:RAMP:SYMmetry %g",
        """Floating point promerty that represents the AFG ramp symmetry, as a percentage.""",
        validator=truncated_range,
        values=[0, 100]

    )

    AFG_dutyCycle = Instrument.control(
        "AFG:SQUare:DUty?", "AFG:SQUare:DUty %g",
        """Floating point property that represents the AFG duty cycle, as a percentage""",
        validator=truncated_range,
        values=[0, 100]
    )

    # todo: refaactor AFG_Arb_Label to a property - how does this work with multiple arguments?
    def AFG_set_arb_label(self, slot, label):
        self.write(f'AFG:ARBitrary:ARB{slot}:LABel {label}')

    def AFG_get_arb_label(self, slot):
        """Queries the waveform label for arbitrary waveform slot 1-4 """
        label = self.ask(f'AFG:ARBitrary:ARB{slot}:LABel?')
