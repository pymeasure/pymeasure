#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands, Guen Prawiroatmodjo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import configparser
import logging
from .results import unique_filename
import numpy as np
import signal
from pymeasure.log import setup_logging

def get_config(filename=''):
    global _CONFIG_FILE
    if filename == '':
        filename = _CONFIG_FILE
    else:
        _CONFIG_FILE = filename
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def init_from_config(filename=''):
    global _CONFIG_FILE
    if filename == '':
        filename = _CONFIG_FILE
    else:
        _CONFIG_FILE = filename
    config = get_config(filename)
    # logging
    if 'Logging' in config._sections.keys():
        log = logging.getLogger()
        setup_logging(log, **config._sections['Logging'])
    # plotting
    if 'rcParams' in config._sections.keys():
        import matplotlib
        for key in config._sections['rcParams']:
            matplotlib.rcParams[key] = eval(config._sections['rcParams'][key])

_CONFIG_FILE = "config.ini"