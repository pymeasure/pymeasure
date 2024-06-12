import time
from pymeasure.instruments.jobinyvon.jobinyvon270m import JY270M
from pyvisa.constants import ControlFlow, Parity, StopBits
import pytest


@pytest.fixture(scope="module")

def init_communication(connected_device_address):
    instr = JY270M(connected_device_address,
                   baud_rate=9600,
                   timeout=300,
                   parity=Parity.none,
                   data_bits=8,
                   stop_bits=StopBits.one,
                   flow_control=ControlFlow.dtr_dsr,
                   write_termination='',
                   read_termination='',
                   includeSCPI=False)
    return instr
    

@pytest.fixture(scope="module")
def jobinyvon270m(init_communication):
    inst = init_communication
    inst.auto_baud()
    return inst


def test_autobaud(init_communication):
    inst = init_communication
    "Ensure the device is in a defined state, e.g. by resetting it."
    initialized = inst.auto_baud()
    i = 0
    while not initialized and i < 2:
        initialized = inst.auto_baud()
        i = i + 1
    if not initialized:
        raise IOError('The spectrometer could not be initialized, please reset the instrument.')


class TestJobinyvon270m:
    """
    Unit tests for the JY270M class.

    This test needs the following setup to work properly:
        - A Jobin Yvon 270M should be connected to the computer via a serial connection.
        - The Jobin Yvon 270M must be turned on.
    """

    def test_motor_init(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.motor_init()
        assert inst.gsteps == inst.max_grating_steps
        assert inst.entrysteps == 0
        assert inst.exitsteps == 0

    def test_move_grating_steps(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.move_grating_steps(35000)
        while inst.motor_busy_check():
            pass
        time.sleep(0.5)
        assert inst.gsteps == 35000
        assert inst.get_grating_wavelength()

    def test_gsteps(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.gsteps = -1000
        while inst.motor_busy_check():
            pass
        time.sleep(0.5)
        assert inst.gsteps == 34000

    def test_move_grating_wavelength(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.move_grating_wavelength(800)
        while inst.motor_busy_check():
            pass
        time.sleep(0.5)
        assert abs(inst.get_grating_wavelength() - 800.0) <= inst.nanometers_in_one_step
        assert inst.gsteps == 25601

    def test_move_entry_slits_steps(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.move_entry_slit_steps(50)
        while inst.motor_busy_check():
            pass
        time.sleep(0.5)
        assert inst.entrysteps == 50

    def test_move_entry_slits_microns(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.move_entry_slit_microns(1000)
        while inst.motor_busy_check():
            pass
        time.sleep(0.5)
        "We test that the entry slit response accuracy is within a certain limit."
        assert abs(inst.get_entry_slit_microns() - 1000.0) <= inst.micrometers_in_one_step

    def test_move_exit_slits_steps(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.move_exit_slit_steps(50)
        while inst.motor_busy_check():
            pass
        time.sleep(0.5)
        assert inst.exitsteps == 50

    def test_move_exit_slits_microns(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.move_exit_slit_microns(1000)
        while inst.motor_busy_check():
            pass
        time.sleep(0.5)
        "We test that the exit slit response accuracy is within a certain limit."
        assert abs(inst.get_exit_slit_microns() - 1000.0) <= inst.micrometers_in_one_step

    def test_entrysteps(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.entrysteps = -30
        while inst.motor_busy_check():
            pass
        time.sleep(0.5)
        assert inst.entrysteps == 530

    def test_exitsteps(self, jobinyvon270m):
        inst = jobinyvon270m
        inst.exitsteps = -30
        while inst.motor_busy_check():
            pass
        time.sleep(0.5)
        assert inst.exitsteps == 530
