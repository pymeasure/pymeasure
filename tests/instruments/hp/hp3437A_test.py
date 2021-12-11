#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 13:19:45 2021

@author: robby
"""
import logging
log = logging.getLogger(__name__)
# log.addHandler(logging.NullHandler())

from pymeasure.log import console_log
from pymeasure.instruments.hp import HP3437A
# from pymeasure.adapters import FakeAdapter

# fa = FakeAdapter()
console_log(log)
svm = HP3437A('GPIB0::24')
#Set timeout for this device to about 60 min = 60000ms
# svm.adapter.connection.timeout = 36000000

svm.number_readings = 5000


# svm.delay = 0.1234567
svm.delay = 0.00001

svm.trigger = "internal"

# svm.SRQ_mask = 7


svm.range= 0.1

svm.talk_ascii = False

print(f"Range {svm.range}")

print(svm.status)

# print(svm.delay)
# handlers = log.handlers[:]
# for handler in handlers:
#     handler.close()
#     log.removeHandler(handler)

    