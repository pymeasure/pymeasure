import pytest

from pymeasure.instruments.attocube import ANC300Controller

#######################
# In order to run the tests, you have to change the superclass of the adapter
# from TelnetAdapter to Mock_TelnetAdapter
#######################


@pytest.fixture
def instr(monkeypatch):
    # monkeypatch.setattr("pymeasure.adapters.TelnetAdapter", Mock_TelnetAdapter)
    instr = ANC300Controller("123", ["a", "b", "c"], "passwd")
    yield instr
    protocol = instr.adapter
    assert protocol._index == len(protocol.comm_pairs), (
        "Unprocessed protocol definitions remain: "
        f"{protocol.comm_pairs[protocol._index:]}.")
    assert protocol._write_buffer == b"", (
        f"Non-empty write buffer: '{protocol._write_buffer}'.")
    assert protocol._read_buffer == b"", (
        f"Non-empty read buffer: '{protocol._read_buffer}'.")


def test_init(instr):
    pass


def test_stepu(instr):
    """Test a setting."""
    instr.adapter.comm_pairs.extend([(b"stepu 1 15\r\n", b"OK")])
    instr.a.stepu = 15


def test_voltage(instr):
    """Test a measurement."""
    instr.adapter.comm_pairs.extend([(b"geto 1\r\n", b"5\r\nOK")])
    assert instr.a.output_voltage == 5
