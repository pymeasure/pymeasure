#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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
import os

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def set_file(filename):
    os.environ['CONFIG'] = filename


def get_config(filename='default_config.ini'):
    if 'CONFIG' in os.environ.keys():
        filename = os.environ['CONFIG']
    config = configparser.ConfigParser()
    config.read(filename)
    return config


# noinspection PyProtectedMember
def set_mpl_rcparams(config):
    if 'matplotlib.rcParams' in config._sections.keys():
        import matplotlib
        for key in config._sections['matplotlib.rcParams']:
            matplotlib.rcParams[key] = eval(config._sections['matplotlib.rcParams'][key])
