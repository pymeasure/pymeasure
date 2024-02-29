from pymeasure.generator import Generator
from pymeasure.instruments.yokogawa.aq6370d import AQ6370D


def main():
    generator = Generator()
    inst = generator.instantiate(AQ6370D, "TCPIP::192.168.123.169::INSTR", "yokogawa.aq6370d")

    inst.initiate()

    inst.abort()

    inst.reference_level = -10

    inst.level_position = 5

    inst.level_position_max()

    inst.sweep_mode = "REPEAT"

    inst.sweep_speed = "1x"

    inst.wavelength_start = 800e-9

    inst.wavelength_stop = 900e-9

    inst.wavelength_center = 850e-9

    inst.wavelength_span = 100e-9

    # inst.active_trace()

    inst.copy_trace("TRB", "TRC")

    inst.delete_trace("TRB")

    inst.get_xdata("TRA")

    inst.get_ydata("TRA")

    inst.resolution_bandwidth = 0.1e-9

    generator.write_file("tests/instruments/yokogawa/test_aq6370d.py")


if __name__ == "__main__":
    main()
