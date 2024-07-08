# This is test code for testing purposes
# Author: Amelie Deshazer
# Date: 2024/06/04
# Purpose: Code is to automate the spectrum analyzer DSA815 to get a spectrum

import pytest
import logging
from pymeasure.test import expected_protocol
from pymeasure.pymeasure.instruments.rigol.firstattempt_draft import DSA815

def test_start_frequency():
    #Not communicating with the ports
    with expected_protocol(DSA815
    , [(":SENSe:FREQuency:STARt?", "3.1415")]
    ) as inst: 
        assert inst.start_frequency == pytest.approx(45)