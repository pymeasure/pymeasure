#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 13:19:45 2021

@author: robby
"""
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments.hp import HP3437A
# from pymeasure.adapters import FakeAdapter

# fa = FakeAdapter()

svm = HP3437A('GPIB0::24')
# # N
# svm.number_readings = 0
# print(f"Number of readings set-string {fa.read()}")
# svm.number_readings = 101
# print(f"Number of readings set-string {fa.read()}")
# svm.number_readings = 1000
# print(f"Number of readings set-string {fa.read()}")
# # svm.number_readings = 12345
# # print(f"Number of readings set-string {fa.read()}")

# # D
# svm.delay = 0
# print(f"Delay set-string {fa.read()}")
# svm.delay = 0.0000001
# print(f"Delay set-string {fa.read()}")
# svm.delay = 0.000123
# print(f"Delay set-string {fa.read()}")
# svm.delay = 0.1234567
# print(f"Delay set-string {fa.read()}")
# svm.delay = 0.999999
# print(f"Delay set-string {fa.read()}")
# # svm.delay = 12.345
# # print(f"Delay set-string {fa.read()}")


# #T
# svm.trigger = "internal"
# print(f"Trigger set-string {fa.read()}")
# svm.trigger = "external"
# print(f"Trigger set-string {fa.read()}")
# svm.trigger = "hold"
# print(f"Trigger set-string {fa.read()}")
# svm.trigger = "manual"
# print(f"Trigger set-string {fa.read()}")
# # svm.trigger = "operator"
# # print(f"Trigger set-string {fa.read()}")


# svm.SRQ_mask = 1
# print(f"SRQ set-string {fa.read()}")
# svm.SRQ_mask = 2
# print(f"SRQ set-string {fa.read()}")
# svm.SRQ_mask = 3
# print(f"SRQ set-string {fa.read()}")
# svm.SRQ_mask = 4
# print(f"SRQ set-string {fa.read()}")
# svm.SRQ_mask = 5
# print(f"SRQ set-string {fa.read()}")
# svm.SRQ_mask = 6
# print(f"SRQ set-string {fa.read()}")
# svm.SRQ_mask = 7
# print(f"SRQ set-string {fa.read()}")
# svm.SRQ_mask = 0
# print(f"SRQ set-string {fa.read()}")
# # svm.SRQ_mask = 8
# # print(f"SRQ set-string {fa.read()}")
# 
# fa._buffer = b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF'
# print(svm.status)
# fa._buffer = b'\xFF\x00\x01\x00\x12\x34\x56'
# print(svm.delay)
# fa._buffer = b'\xFF\x12\x34\x01\x23\x45\x67'
# print(svm.delay)
# fa._buffer = b'\xFF\x12\x34\x01\x29\x39\x49'
# print(svm.number_readings)

# svm.range= 0.1
# print(f"Range set-string {fa.read()}")
# svm.range= 1
# print(f"Range set-string {fa.read()}")
# svm.range= 10
# print(f"Range set-string {fa.read()}")
# fa._buffer = b'\xAA\x12\x34\x01\x29\x39\x49'
# print(f"Range readback {svm.range}")
# fa._buffer = b'\xAA\x12\x34\x01\x29\x39\x49'
# print(f"Trigger readback {svm.trigger}")
