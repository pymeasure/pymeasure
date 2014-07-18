#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Generic classes and functions for experiment data
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from os.path import exists, basename
from datetime import datetime
import re

def uniqueFilename(directory, prefix='DATA', ext='csv'):
    """ Returns a unique filename based on the directory and prefix
    """
    date = datetime.now().strftime("%Y%m%d")
    i = 1
    filename = "%s%s%s_%d.%s" % (directory, prefix, date, i, ext)
    while exists(filename):
        i += 1
        filename = "%s%s%s_%d.%s" % (directory, prefix, date, i, ext)  
    return filename
