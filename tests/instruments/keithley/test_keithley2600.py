import unittest
from unittest.mock import MagicMock
from pymeasure.instruments import Instrument
from pymeasure.instruments.keithley.keithley_2600 import Channel


class TestChannelOutputOffMode(unittest.TestCase):
    def setUp(self):
        # Mock the Instrument class
        self.mock_instrument = MagicMock(spec=Instrument)

        # Create an instance of the Channel class with the mocked instrument
        self.channel = Channel(self.mock_instrument, 'a')

    def test_output_off_mode_normal(self):
        """Test setting the output_off_mode to 'normal'."""
        self.channel.output_off_mode = 'normal'
        self.mock_instrument.write.assert_called_with('smua.source.offmode=0')

    def test_output_off_mode_zero(self):
        """Test setting the output_off_mode to 'zero'."""
        self.channel.output_off_mode = 'zero'
        self.mock_instrument.write.assert_called_with('smua.source.offmode=1')

    def test_output_off_mode_high_z(self):
        """Test setting the output_off_mode to 'high_z'."""
        self.channel.output_off_mode = 'high_z'
        self.mock_instrument.write.assert_called_with('smua.source.offmode=2')

    def test_invalid_output_off_mode(self):
        """Test setting the output_off_mode to an invalid value."""
        with self.assertRaises(ValueError):
            self.channel.output_off_mode = 'invalid_mode'


if __name__ == '__main__':
    unittest.main()
