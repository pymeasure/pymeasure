#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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


from setuptools import setup, find_packages

setup(
    name='PyMeasure',
    version='0.4.4',
    author='PyMeasure Developers',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/ralph-group/pymeasure',
    download_url = 'https://github.com/ralph-group/pymeasure/tarball/v0.4.4',
    license='MIT License',
    description='Scientific measurement library for instruments, experiments, and live-plotting',
    long_description=open('README.rst').read() + "\n\n" + open('CHANGES.txt').read(),
    install_requires=[
        "Numpy >= 1.6.1",
        "pandas >= 0.14",
        "pyvisa >= 1.8",
        "pyserial >= 2.7",
        "pyqtgraph >= 0.9.10"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering",
    ],
    keywords="measure instrument experiment control automate graph plot"
)
