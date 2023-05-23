import logging
import sys
import time
from time import sleep

from pymeasure.instruments.wenworthlabs import S200

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def main() -> int:
    probe_table = S200("GPIB0::28::INSTR")
    try:
        t2(probe_table)
    except Exception:
        print("Exception", Exception.mro(), Exception.with_traceback())

    return 0


def t1(probe_table):
    """
    :type probe_table:S200
    """
    while True:
        print(probe_table.status_byte)


def t2(probe_table):
    """
    :type probe_table:S200
    """
    while True:
        time.sleep(0.5)
        probe_table.lamp_on = True
        time.sleep(0.5)
        probe_table.lamp_on = False
    # probe_table.t()


def t3(probe_table):
    """
    :type probe_table:S200
    """
    while True:
        time.sleep(0.5)
        probe_table.lamp_on_2 = 'LI0'
        time.sleep(0.5)
        probe_table.lamp_on_2 = 'LI1'

###############################################################################################3

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys
