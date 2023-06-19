# -*- coding: utf-8 -*-
"""
Created the 19/06/2023

@author: Sebastien Weber
"""

error_codes = {
    '0': 'Status OK',
    '1': 'Communication Timeout',
    '2': 'Mechanical Timeout',
    '3': 'Command Error',
    '4': 'Value Out of Range',
    '5': 'Module Isolated',
    '6': 'Module Out of Isolation',
    '7': 'Initialisation Error',
    '8': 'Thermal Error',
    '9': 'Busy',
    '10': 'Sensor Error',
    '11': 'Motor Error',
    '12': 'Out of Range',
    '13': 'Over Current Error',
}


class ExternalDeviceNotFound(IOError):
    pass


class StatusError(IOError):
    def __init__(self, message):
        super().__init__(message)
