# -*- coding: utf-8 -*-
"""
Created the 20/06/2023

@author: Sebastien Weber
"""
import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.thorlabs.elliptec_utils.base import ElliptecController, MotorChannel


def test_init():
    with expected_protocol(
            ElliptecController,
            [],
    ):
        pass  # Verify the expected communication.
