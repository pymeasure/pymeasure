"""
This example demonstrates how to make a graphical interface, and uses
a random number generator to simulate data so that it does not require
an instrument to use.

Run the program by changing to the directory containing this file and calling:

python gui.py

"""

# import sys
# import random
# import tempfile
# from time import sleep

# from datetime import datetime, timedelta

# from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.instruments.lecroy.lecroyLabMaster10ZiA import LabMaster10ZiA
import pyvisa
import logging

log = logging.getLogger("")
log.addHandler(logging.NullHandler())


if __name__ == "__main__":

    rm = pyvisa.ResourceManager()
    resource_list = rm.list_resources()
    # ip = resource_list[0]
    ip = "TCPIP::10.1.10.85::inst0::INSTR"
    scope = LabMaster10ZiA(ip)
    scope.autosetup()
    scope.toggle_trace("C1", "off")
    scope.toggle_trace("C2", "on")
    scope.toggle_trace("C3", "on")
    scope.trig_setup("auto")
    scope.trigger_select = "c2"
    scope.sample_mode("RealTime")
    scope.download_waveform(source="C2", requested_points=1e5)

    ...
    scope.download_waveform(source="C3", requested_points=0, sparsing=0)
    scope.ch(1)
    chs = scope.current_configuration(scope)
    print(chs)
    print("here")
