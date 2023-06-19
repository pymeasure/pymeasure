# -----------------------------------------------------------------------------
# Summary:		Implementation of LeCroyDSO Control class
# Authors:		Ashok Bruno
# Started:		10/21/2022
# Copyright 2022-2025 Nubis Communications Corporation. All Rights Reserved.
# -----------------------------------------------------------------------------


from pymeasure.instruments import Instrument
from pymeasure.instruments.agiltron.adapters import AgiltronConsoleAdapter
import time

# ------------------------------------------------------------------------------------


class AgiltronMEMS1xN(Instrument):
    """#! finish"""

    def __init__(self, host="192.168.1.200", port=23, uname="root", passwd="fs19681086", **kwargs):
        super().__init__(
            AgiltronConsoleAdapter(host, port=port),
            name="Agiltron MEMS 1xN Optical Switch",
            includeSCPI=False,
            **kwargs,
        )

        self.query_delay = 0.1
        if self.adapter.connection is not None:
            self.adapter.connection.timeout = 3000
        self._seconds_since_last_write = 0

        self.login(uname, passwd)

    def login(self, uname, passwd):
        # get username input
        self.read()
        # enter username input
        self.write(command=uname)
        # get password input
        self.read()
        # enter password input\
        self.write(command=passwd)

    def read(self):
        self.adapter.read()
        time.sleep(self.query_delay)

    def write(self, command):
        self.adapter.write(command)
        time.sleep(self.query_delay)

    def switch_channel(self, channel):
        self.write(f"CARD -c 04 S01_{channel}")
        time.sleep(self.query_delay)
