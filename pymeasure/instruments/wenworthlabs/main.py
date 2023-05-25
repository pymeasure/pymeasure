import logging
import sys
import time

from pymeasure.instruments.wenworthlabs import S200

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def main() -> int:
    probe_table = S200("GPIB0::28::INSTR")
    # test_lamp(probe_table)
    # test_info(probe_table)
    test_location(probe_table)

    return 0


def test_lamp(probe_table):
    """
    :type probe_table:S200
    """
    while True:
        time.sleep(1.0)
        probe_table.lamp_on = True
        time.sleep(1.0)
        probe_table.lamp_on = False

def test_info(probe_table):
    """
    :type probe_table:S200
    """
    print("Model Id: ", probe_table.model_id)
    print("Serial Number: ", probe_table.serial_number)
    print("Software Version Number: ", probe_table.software_version_number)
    print("Hardware Build: ", probe_table.hardware_build)

def test_location(probe_table):
    """
    :type probe_table:S200
    """
    while True:
        probe_table.move_to_probing_zone_centre_position()
        time.sleep(3)
        probe_table.move_to_manual_load_position()
        time.sleep(3)

###############################################################################################3

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys
