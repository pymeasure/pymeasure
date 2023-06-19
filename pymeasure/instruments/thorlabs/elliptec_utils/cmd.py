# -*- coding: utf-8 -*-
"""
Created the 19/06/2023

@author: Sebastien Weber
Taken and adapted from the elliptec package by David Roesel (with his permission): https://david.roesel.cz/en/

This file contains a dictionary of commands that the devices can accept in
three different categories: get, set, move. For each command, it returns the
instruction code to send to the device.
"""

# TODO: Each type of device should get it's own list of supported commands.

get_ = {
    'info': b'in',
    'status': b'gs',
    'position': b'gp',
    'stepsize': b'gj',
    'home_offset': b'go',
    'motor_1_info': b'i1',
    'motor_2_info': b'i2',
}

set_ = {
    'stepsize': b'sj',
    'isolate': b'is',
    'address': b'ca',
    'home_offset': b'so'
}

mov_ = {
    'home_clockwise': b'ho0',
    'home_anticlockwise': b'ho1',
    'forward': b'fw',
    'backward': b'bw',
    'absolute': b'ma',
    'relative': b'mr'
}


def commands():
    return {"get": get_, "set": set_, "move": mov_}


if __name__ == '__main__':
    cmds = commands()
    print(cmds)
