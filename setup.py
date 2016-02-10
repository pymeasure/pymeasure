"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from setuptools import setup

setup(
    name='PyMeasure',
    version='0.2',
    author='Colin Jermain, Graham Rowlands',
    packages=[
        'pymeasure', 'pymeasure.instruments',
        'pymeasure.adapters', 'pymeasure.display',
        'pymeasure.experiment'
    ],
    scripts=[],
    url='https://github.com/ralph-group/pymeasure',
    license='LICENSE.txt',
    description='Measurement library for instrument communication, procedure execution, and live-plotting',
    long_description=open('README.md').read(),
    install_requires=[
        "Numpy >= 1.6.1",
        "pandas >= 0.14",
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
    ]
)
