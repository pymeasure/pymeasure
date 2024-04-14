from pymeasure.instruments import Instrument, SCPIUnknownMixin, Channel
from pymeasure.adapters import SerialAdapter
from pymeasure.instruments.validators import strict_discrete_range, strict_range, strict_discrete_set

def step_validator(step):
    """Creates a strict_discrete_range with the specified step"""
    return lambda x, y: strict_discrete_range(x, y, step)

class BaseAWGChannel(Channel):
    WAVEFORMS = {"SINE": 0, 
                 "TRIANGLE": 1, 
                 "SQUARE": 2}

    waveform = Instrument.setting("{ch}w%i",
                                  validator= strict_discrete_set,
                                  map_values=True,
                                  values=WAVEFORMS,
                                  )
    
    frequency = Instrument.setting("{ch}f%.9i",
                                   validator=step_validator(1),
                                   values=(0, 100000000),
                                   set_process=lambda x: x//10
                                   )
    
    amplitude = Instrument.setting("{ch}a%f",
                                   validator=step_validator(0.1),
                                   values=(0.1, 20),
                                   )
    
    offset = Instrument.setting("{ch}o%f",
                                validator=step_validator(0.1),
                                values=(-10, 10)
                                )
    
    duty_cycle = Instrument.setting("{ch}d%i",
                                    validator=step_validator(1),
                                    values=(1, 99)
                                    )


class FY3200S(Instrument, SCPIUnknownMixin):
    '''Class to control the Feeltech FY3200S arbitrary waveform generator'''

    def __init__(self, address, includeSCPI=None, preprocess_reply=None, **kwargs):
        super().__init__(SerialAdapter(address, write_termination="0x0a"), 
                         "Feeltech FY3200S", 
                         includeSCPI, 
                         preprocess_reply, 
                         **kwargs)
    

    