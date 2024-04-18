import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.feeltech import FY3200S

def test_init():
    with expected_protocol(
        FY3200S,
        []
    ) as instr:
        pass

def test_waveform():
    with expected_protocol(
        FY3200S,
        [("bw1", None),
         ("dw1", None)]
    ) as instr:
        instr.main_channel.waveform = "SQUARE"
        instr.subsidiary_channel.waveform = "SQUARE"
       
def test_amplitude():
    with expected_protocol(
        FY3200S,
        [("ba1.5", None),
         ("da1.5", None)]
    ) as instr:
        instr.main_channel.amplitude = 1.5
        instr.subsidiary_channel.amplitude = 1.5
                
def test_offset():
    with expected_protocol(
        FY3200S,
        [("bo1.5", None),
         ("do1.5", None)]
    ) as instr:
        instr.main_channel.offset = 1.5
        instr.subsidiary_channel.offset = 1.5

def test_frequency():
    with expected_protocol(
        FY3200S,
        [("bf000010000", None),
         ("b\ncf", "cf000010000"),
         ("df000010000", None),
         ("d\ncf", "cf000010000")]
    ) as instr:
        instr.main_channel.frequency = 100
        assert instr.main_channel.frequency == 100
        instr.subsidiary_channel.frequency = 100
        assert instr.subsidiary_channel.frequency == 100
        
def test_duty_cycle():
    with expected_protocol(
        FY3200S,
        [("bd50", None),
         ("b\ncd", "cd50"),
         ("dd50", None),
         ("d\ncd", "cd50")]
    ) as instr:
        instr.main_channel.duty_cycle = 50
        assert instr.main_channel.duty_cycle == 50
        instr.subsidiary_channel.duty_cycle = 50
        assert instr.subsidiary_channel.duty_cycle == 50
        
def test_phase():
    with expected_protocol(
        FY3200S,
        [("dp135", None)]
    ) as instr:
        instr.subsidiary_channel.phase = 135
        
def test_sweep():
    with expected_protocol(
        FY3200S,
        [("bt05", None),
         ("b\nct", "ct05"),
         ("bb000100000", None),
         ("be000300000", None),
         ("bm1", None),
         ("br1", None),
         ("br0", None)]
    ) as instr:
        instr.main_channel.sweep_time = 5
        assert instr.main_channel.sweep_time == 5
        instr.main_channel.sweep_beginning_frequency = 1000
        instr.main_channel.sweep_end_frequency = 3000
        instr.main_channel.sweep_mode = "LOG"
        instr.main_channel.start_sweep()
        instr.main_channel.pause_sweep()
        
def test_freqeuncy_counter():
    with expected_protocol(
        FY3200S,
        [("ce", "ce000100000"),
         ("cc", "cc000000547")]
    ) as instr:
        assert instr.frequency == 1000
        assert instr.count == 547
        
def test_save_load():
    with expected_protocol(
        FY3200S,
        [("bs9", None),
         ("bl9", None)]
    ) as instr:
        instr.save(9)
        instr.load(9)
        
