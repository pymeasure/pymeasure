from unittest.mock import Mock, call

import pytest

from pymeasure.adapters.adapter import FakeAdapter
from pymeasure.instruments.keithley.keithley2602B import Keithley2602B


@pytest.fixture
def driver(monkeypatch) -> Keithley2602B:
    def mock_adapter(self, *args, **kwargs):
        tmp_adapter = FakeAdapter()
        monkeypatch.setattr(tmp_adapter, "ask", mock_ask)
        mock_write = Mock()
        monkeypatch.setattr(tmp_adapter, "write", mock_write)
        return tmp_adapter

    def mock_ask(cmd: str):
        if cmd == "waitcomplete() print([[1]])":
            return "1"
        elif cmd == "print(errorqueue.next())":
            return "0"
        elif (
            cmd
            == "print([[Keithley Instruments, Model]]..localnode.model..[[,]]..localnode.serialno.. [[, ]]..localnode.revision))"
        ):
            return "Keithley"
        else:
            return None

    monkeypatch.setattr(Keithley2602B, "connect", mock_adapter)
    driver = Keithley2602B(hostname="0.0.0.0")
    yield driver


class TestKeithley2602B:
    def test_get_ID(self, driver):
        response = driver.get_id()
        assert response.startswith(driver.id_starts_with)

    def test_validator(self, driver):
        with pytest.raises(ValueError):
            driver.ChA.compliance_voltage = 1

    def test_status(self, driver):
        assert driver.status == "ok: ON"

    @pytest.mark.parametrize(
        "current",
        [-1, 0.5, 1],
    )
    def test_set_source_current(self, driver, monkeypatch, current):

        mock_write = Mock()
        monkeypatch.setattr(driver.adapter, "write", mock_write)
        driver.ChA.source_current = current
        mock_write.assert_has_calls([call(f"smua.source.leveli={current:f}")])
