#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

import pytest
from contextlib import nullcontext as does_not_raise

from pymeasure.test import expected_protocol
from pymeasure.instruments.formfactor.velox import Velox


class TestChuck:
    def test_move_contact(self):
        with expected_protocol(
            Velox,
            [("MoveChuckContact 100", "0:")]
        ) as inst:
            assert "" == inst.chuck.move_contact()

    def test_move_align(self):
        with expected_protocol(
            Velox,
            [("MoveChuckAlign 1", "0:")]
        ) as inst:
            assert "" == inst.chuck.move_align(1)

    def test_move_separation(self):
        with expected_protocol(
            Velox,
            [("MoveChuckSeparation 100", "0:")]
        ) as inst:
            assert "" == inst.chuck.move_separation()

    @pytest.mark.parametrize("pos_ref, mapping", [
                             ("home", "H"),
                             ("Zero", "Z"),
                             ("Relative", "R"),
                             ("Center", "C"),
                             ("DieHome", "D"),
                             ])
    def test_move_index(self, pos_ref, mapping):
        with expected_protocol(
            Velox,
            [(f"MoveChuckIndex 1 2 {mapping} 100", "0:"),
             ]
        ) as inst:
            assert "" == inst.chuck.move_index(1, 2, pos_ref)

    @pytest.mark.parametrize("unit, mapping", [
                             ("microns", "Y"),
                             ("mils", "I"),
                             ("jogs", "J"),
                             ("encoder", "E"),
                             ("index", "X"),
                             ])
    def test_move(self, unit, mapping):
        with expected_protocol(
            Velox,
            [(f"MoveChuck 199 -23.6 C {mapping} 100", "0:"),
             ]
        ) as inst:
            assert "" == inst.chuck.move(199, -23.6, "center", unit)

    def test_index(self):
        with expected_protocol(
            Velox,
            [(f"SetChuckIndex {100:f} {200:f} Y", "0:"),
             ("ReadChuckIndex Y", "0:100 200"),
             ]
        ) as inst:
            inst.chuck.index = (100, 200)
            assert [100, 200] == inst.chuck.index


class TestWaferMap:
    def test_step_first_die(self):
        with expected_protocol(
            Velox,
            [("StepFirstDie", "0: 4 6 1")]
        ) as inst:
            assert [4, 6, 1] == inst.wafermap.step_first_die()

    def test_step_next_die_no_args(self):
        with expected_protocol(
            Velox,
            [("StepNextDie", "0: 1 2 3"),
             ]
        ) as inst:
            assert [1, 2, 3] == inst.wafermap.step_next_die()

    @pytest.mark.parametrize("coordinates", [
        "5 6 1",
        "5,6 1",
        "5,6;1",
        (5, "6", 1),  # tuple
        [5, 6, 1],  # list
        ])
    def test_step_next_die_single_arg(self, coordinates):
        with expected_protocol(
            Velox,
            [("StepNextDie 5 6 1", "0: 5 6 1"),
             ]
        ) as inst:
            assert [5, 6, 1] == inst.wafermap.step_next_die(coordinates)

    def test_step_next_die_multi_args(self):
        with expected_protocol(
            Velox,
            [("StepNextDie 1", "0: 1 6 0 0"),
             ("StepNextDie 1 2", "0: 1 2 0 1"),
             ("StepNextDie 1 2 3", "0: 1 2 3 9"),
             ]
        ) as inst:
            assert [1, 6, 0, 0] == inst.wafermap.step_next_die(1)
            assert [1, 2, 0, 1] == inst.wafermap.step_next_die(1, 2)
            assert [1, 2, 3, 9] == inst.wafermap.step_next_die(1, "2", [3])  # mixed types

    @pytest.mark.parametrize("enabled, mapping", [
                             (True, 1),
                             (False, 0),
                             ])
    def test_enabled(self, enabled, mapping):
        with expected_protocol(
            Velox,
            [("IsAppRegistered WaferMap", f"{mapping}")]
        ) as inst:
            assert enabled == inst.wafermap.enabled


class TestVelox:
    def test_error(self):
        with pytest.raises(ConnectionError):
            with expected_protocol(
                Velox,
                [("*IDN?", "7: Error Message")]
            ) as inst:
                inst.id

    def test_expected_error(self):
        with does_not_raise(ConnectionError):
            with expected_protocol(
                Velox,
                [("StepNextDie", "703: End of wafer.")]
            ) as inst:
                inst.wafermap.step_next_die()

    def test_options(self):
        with pytest.raises(NotImplementedError):
            with expected_protocol(
                Velox,
                [("*OPT?", "Fake options")]
            ) as inst:
                inst.options

    def test_version(self):
        with expected_protocol(
            Velox,
            [("ReportSoftwareVersion", "0: 1.2.33.44")]
        ) as inst:
            assert "1.2.33.44" == inst.version
