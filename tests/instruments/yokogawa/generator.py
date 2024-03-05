from pathlib import Path
from time import sleep

from pymeasure.generator import Generator
from pymeasure.instruments.yokogawa.aq6370d import AQ6370D


def main():
    generator = Generator()
    inst = generator.instantiate(AQ6370D, "TCPIP::192.168.123.169::INSTR", "yokogawa.aq6370d")

    inst.reset()

    inst.wavelength_start = 800e-9
    inst.wavelength_stop = 900e-9
    assert inst.wavelength_span == 100e-9
    assert inst.wavelength_center == 850e-9

    inst.reference_level = -10
    assert inst.reference_level == -10

    inst.set_level_position_to_max()
    assert inst.level_position == 8

    inst.sweep_mode = "REPEAT"
    inst.initiate_sweep()
    assert inst.sweep_mode == "REPEAT"

    inst.sweep_speed = "1x"
    assert inst.sweep_speed == "1x"
    inst.sweep_speed = "2x"
    assert inst.sweep_speed == "2x"

    inst.automatic_sample_number = False
    inst.wavelength_span = 10e-9
    inst.resolution_bandwidth = 1e-9
    inst.sample_number = 101

    sleep(1)
    assert len(inst.get_xdata("TRA")) == 101
    assert len(inst.get_ydata("TRA")) == 101

    generator.write_file(Path(__file__).parent / "test_aq6370d.py")


if __name__ == "__main__":
    main()
