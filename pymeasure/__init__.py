#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
import warnings

# Maximally flexible approach to obtain version numbers, based on this approach:
# https://github.com/pypa/setuptools_scm/issues/143#issuecomment-672878863
# Sadly, this does not work with editable installs, which bake in version info on installation.
# see also https://github.com/pyusb/pyusb/pull/307#issuecomment-650797688
try:
    # If a user has setuptools_scm installed, assume they want the most up to date version string.
    # Alternatively, we could use a dummy dev module that is never packaged whose presence signals
    # that we are in an editable install/repo, see https://github.com/pycalphad/pycalphad/pull/341
    import setuptools_scm
    __version__ = setuptools_scm.get_version(root='..', relative_to=__file__)
    del setuptools_scm
except (ImportError, LookupError):
    # Setuptools_scm was not found, or it could not find a version, so use installation metadata.
    from importlib.metadata import version, PackageNotFoundError

    try:
        __version__ = version("pymeasure")
        # Alternatively, if the current approach is too slow, we could add
        # 'write_to = "pymeasure/_version.py"' in pyproject.toml and use the generated file here:
        # from ._version import version as __version__
    except PackageNotFoundError:
        warnings.warn('Could not find pymeasure version, it does not seem to be installed. '
                      'Either install it (editable or full) or install setuptools_scm')
        __version__ = '0.0.0'
    finally:
        del version, PackageNotFoundError
