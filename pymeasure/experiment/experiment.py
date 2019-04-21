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

import logging

log = logging.getLogger()
log.addHandler(logging.NullHandler())

try:
    from IPython import display
except ImportError:
    log.warning("IPython could not be imported")

from .results import unique_filename
from .config import get_config, set_mpl_rcparams
from pymeasure.log import setup_logging, console_log
from pymeasure.experiment import Results, Worker
from .parameters import Measurable
import time, signal
import numpy as np
import tempfile
import gc


def get_array(start, stop, step):
    """Returns a numpy array from start to stop"""
    step = np.sign(stop - start) * abs(step)
    return np.arange(start, stop + step, step)


def get_array_steps(start, stop, numsteps):
    """Returns a numpy array from start to stop in numsteps"""
    return get_array(start, stop, (abs(stop - start) / numsteps))


def get_array_zero(maxval, step):
    """Returns a numpy array from 0 to maxval to -maxval to 0"""
    return np.concatenate((np.arange(0, maxval, step), np.arange(maxval, -maxval, -step),
                           np.arange(-maxval, 0, step)))


def create_filename(title):
    """
    Create a new filename according to the style defined in the config file.
    If no config is specified, create a temporary file.
    """
    config = get_config()
    if 'Filename' in config._sections.keys():
        filename = unique_filename(suffix='_%s' % title, **config._sections['Filename'])
    else:
        filename = tempfile.mktemp()
    return filename


class Experiment(object):
    """ Class which starts logging and creates/runs the results and worker processes.

    .. code-block:: python

        procedure = Procedure()
        experiment = Experiment(title, procedure)
        experiment.start()
        experiment.plot_live('x', 'y', style='.-')

        for a multi-subplot graph:

        import pylab as pl
        ax1 = pl.subplot(121)
        experiment.plot('x','y',ax=ax1)
        ax2 = pl.subplot(122)
        experiment.plot('x','z',ax=ax2)
        experiment.plot_live()

    :var value: The value of the parameter

    :param title: The experiment title
    :param procedure: The procedure object
    :param analyse: Post-analysis function, which takes a pandas dataframe as input and
        returns it with added (analysed) columns. The analysed results are accessible via
        experiment.data, as opposed to experiment.results.data for the 'raw' data.
    :param _data_timeout: Time limit for how long live plotting should wait for datapoints.
    """

    def __init__(self, title, procedure, analyse=(lambda x: x)):
        self.title = title
        self.procedure = procedure
        self.measlist = []
        self.port = 5888
        self.plots = []
        self.figs = []
        self._data = []
        self.analyse = analyse
        self._data_timeout = 10

        config = get_config()
        set_mpl_rcparams(config)
        if 'Logging' in config._sections.keys():
            self.scribe = setup_logging(log, **config._sections['Logging'])
        else:
            self.scribe = console_log(log)
        self.scribe.start()

        self.filename = create_filename(self.title)
        log.info("Using data file: %s" % self.filename)

        self.results = Results(self.procedure, self.filename)
        log.info("Set up Results")

        self.worker = Worker(self.results, self.scribe.queue, logging.DEBUG)
        log.info("Create worker")

    def start(self):
        """Start the worker"""
        log.info("Starting worker...")
        self.worker.start()

    @property
    def data(self):
        """Data property which returns analysed data, if an analyse function
        is defined, otherwise returns the raw data."""
        self._data = self.analyse(self.results.data.copy())
        return self._data

    def wait_for_data(self):
        """Wait for the data attribute to fill with datapoints."""
        t = time.time()
        while self.data.empty:
            time.sleep(.1)
            if (time.time() - t) > self._data_timeout:
                log.warning('Timeout, no data received for liveplot')
                return False
        return True

    def plot_live(self, *args, **kwargs):
        """Live plotting loop for jupyter notebook, which automatically updates
        (an) in-line matplotlib graph(s). Will create a new plot as specified by input
        arguments, or will update (an) existing plot(s)."""
        if self.wait_for_data():
            if not (self.plots):
                self.plot(*args, **kwargs)
            while not self.worker.should_stop():
                self.update_plot()
            display.clear_output(wait=True)
            if self.worker.is_alive():
                self.worker.terminate()
            self.scribe.stop()

    def plot(self, *args, **kwargs):
        """Plot the results from the experiment.data pandas dataframe. Store the
        plots in a plots list attribute."""
        if self.wait_for_data():
            kwargs['title'] = self.title
            ax = self.data.plot(*args, **kwargs)
            self.plots.append({'type': 'plot', 'args': args, 'kwargs': kwargs, 'ax': ax})
            if ax.get_figure() not in self.figs:
                self.figs.append(ax.get_figure())
            self._user_interrupt = False

    def clear_plot(self):
        """Clear the figures and plot lists."""
        for fig in self.figs:
            fig.clf()
            pl.close()
        self.figs = []
        self.plots = []
        gc.collect()

    def update_plot(self):
        """Update the plots in the plots list with new data from the experiment.data
        pandas dataframe."""
        try:
            tasks = []
            self.data
            for plot in self.plots:
                ax = plot['ax']
                if plot['type'] == 'plot':
                    x, y = plot['args'][0], plot['args'][1]
                    if type(y) == str:
                        y = [y]
                    for yname, line in zip(y, ax.lines):
                        self.update_line(ax, line, x, yname)
                if plot['type'] == 'pcolor':
                    x, y, z = plot['x'], plot['y'], plot['z']
                    update_pcolor(ax, x, y, z)

            display.clear_output(wait=True)
            display.display(*self.figs)
            time.sleep(0.1)
        except KeyboardInterrupt:
            display.clear_output(wait=True)
            display.display(*self.figs)
            self._user_interrupt = True

    def pcolor(self, xname, yname, zname, *args, **kwargs):
        """Plot the results from the experiment.data pandas dataframe in a pcolor graph.
        Store the plots in a plots list attribute."""
        title = self.title
        x, y, z = self._data[xname], self._data[yname], self._data[zname]
        shape = (len(y.unique()), len(x.unique()))
        diff = shape[0] * shape[1] - len(z)
        Z = np.concatenate((z.values, np.zeros(diff))).reshape(shape)
        df = pd.DataFrame(Z, index=y.unique(), columns=x.unique())
        ax = sns.heatmap(df)
        pl.title(title)
        pl.xlabel(xname)
        pl.ylabel(yname)
        ax.invert_yaxis()
        pl.plt.show()
        self.plots.append(
            {'type': 'pcolor', 'x': xname, 'y': yname, 'z': zname, 'args': args, 'kwargs': kwargs,
             'ax': ax})
        if ax.get_figure() not in self.figs:
            self.figs.append(ax.get_figure())

    def update_pcolor(self, ax, xname, yname, zname):
        """Update a pcolor graph with new data."""
        x, y, z = self._data[xname], self._data[yname], self._data[zname]
        shape = (len(y.unique()), len(x.unique()))
        diff = shape[0] * shape[1] - len(z)
        Z = np.concatenate((z.values, np.zeros(diff))).reshape(shape)
        df = pd.DataFrame(Z, index=y.unique(), columns=x.unique())
        cbar_ax = ax.get_figure().axes[1]
        sns.heatmap(df, ax=ax, cbar_ax=cbar_ax)
        ax.set_xlabel(xname)
        ax.set_ylabel(yname)
        ax.invert_yaxis()

    def update_line(self, ax, hl, xname, yname):
        """Update a line in a matplotlib graph with new data."""
        del hl._xorig, hl._yorig
        hl.set_xdata(self._data[xname])
        hl.set_ydata(self._data[yname])
        ax.relim()
        ax.autoscale()
        gc.collect()

    def __del__(self):
        self.scribe.stop()
        if self.worker.is_alive():
            self.worker.recorder_queue.put(None)
            self.worker.monitor_queue.put(None)
            self.worker.stop()
