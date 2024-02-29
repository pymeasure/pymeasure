from pymeasure.generator import Generator
from pymeasure.instruments.yokogawa.aq6370d import AQ6370D


def main():
    generator = Generator()
    inst = generator.instantiate(AQ6370D, "TCPIP::192.168.123.169::INSTR", "yokogawa.aq6370d")

    inst.resolution_bandwidth = 0.1e-9

    generator.write_file("tests/instruments/yokogawa/test_aq6370d.py")


if __name__ == "__main__":
    main()
