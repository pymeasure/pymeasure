from pymeasure.instruments import Instrument, Channel
import numpy as np


class GP_PressureChannel(Channel):
    """
    Channel of the GP350UHV vacuum sensor for pressure measurement.

    Each channel corresponds to a filament or display output of the sensor.
    """

    pressure = Instrument.measurement(
        "#RD{ch}",
        """Measure the current pressure in mbar (float).""",
        preprocess_reply=lambda reply: reply.lstrip("* ").strip(),
        get_process=lambda r: np.nan if float(r) == 9.90e9 else float(r),
    )


class GP350UHV(Instrument):
    """
    Representation of the GP350UHV Vacuum Sensor.

    Provides access to multiple pressure channels corresponding to filaments
    and display outputs. Each channel can be queried for its current pressure
    in mbar.
    """

    def __init__(self, adapter, name="GP350UHV Vacuum Sensor", **kwargs):
        """
        Initialize the GP350UHV instrument.

        Parameters
        ----------
        adapter : Adapter
            Communication adapter (e.g., SerialAdapter, VISAAdapter).
        name : str, optional
            Name of the instrument, default is "GP350UHV Vacuum Sensor".
        **kwargs
            Additional keyword arguments passed to the Instrument base class.
        """
        super().__init__(adapter, name, includeSCPI=False, **kwargs)

    filament_1 = Instrument.ChannelCreator(GP_PressureChannel, "1")
    """Measure the pressure from filament 1 in mbar (float)."""

    filament_2 = Instrument.ChannelCreator(GP_PressureChannel, "2")
    """Measure the pressure from filament 2 in mbar (float)."""

    display_middle = Instrument.ChannelCreator(GP_PressureChannel, "A")
    """Measure the pressure from the middle display (channel A) in mbar (float)."""

    display_bottom = Instrument.ChannelCreator(GP_PressureChannel, "B")
    """Measure the pressure from the bottom display (channel B) in mbar (float)."""
