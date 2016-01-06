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
from .results import unique_filename
from .config import get_config
from pymeasure.log import get_log, setup_logging
from pymeasure.experiment import Results, Worker
import time, signal
import numpy as np
import gc
log = get_log()

def get_array(start, stop, step):
    '''Returns a numpy array from start to stop'''
    step = np.sign(stop-start)*abs(step)
    return np.arange(start, stop+step, step)

def get_array_steps(start, stop, numsteps):
    '''Returns a numpy array from start to stop in numsteps'''
    return get_array(start, stop, (abs(stop-start)/numsteps))

def get_array_zero(maxval, step):
    '''Returns a numpy array from 0 to maxval to -maxval to 0'''
    return np.concatenate((np.arange(0,maxval,step), np.arange(maxval, -maxval, -step), np.arange(-maxval, step, step)))

def create_filename(title):
    filename = unique_filename(suffix='_%s' %title, **get_config()._sections['Filename'])
    return filename

class Measurable(object):
    '''Measurable variable for getting e.g. instrument parameters'''
    def __init__(self, name, fget, units=None, measure=True, **kwargs):
        self.name = name
        self.units = units
        self.measure = measure
        self.fget = fget
        self.__class__.value = property(fget)

class Experiment(Worker):
    '''Class for running procedures.'''
    def __init__(self, title, procedure, logging=True):
        self.title = title
        self.procedure = procedure
        self.measlist = []
        self.port = 5888
        self.plots = []
        self.figs = []
        self._data = []

        self.gen_measurement()

        self.filename = create_filename(self.title)
        log.info("Using data file: %s" % self.filename)

        self.results = Results(self.procedure, self.filename)
        log.info("Set up Results")

        super(Experiment, self).__init__(self.results, self.port)

    @property
    def data(self):
        self._data = self.results.data
        return self._data

    def gen_measurement(self):
        '''Create MEASURE and DATA_COLUMNS variables for measure method.
        '''
        if not hasattr(self.procedure,'measure'):
            self.procedure.measure = self.measure
            self.procedure.MEASURE = {}
            for item in dir(self.procedure):
                parameter = getattr(self.procedure, item)
                if isinstance(parameter, Measurable):
                    if parameter.measure:
                        self.procedure.MEASURE.update({item: parameter.fget})
            if self.procedure.DATA_COLUMNS == []:
                self.procedure.DATA_COLUMNS = self.procedure.MEASURE.keys()

    def get_datapoint(self):
        params = self.procedure.MEASURE
        data = {key:params[key]() for key in params}
        return data

    def measure(self):
        data = self.get_datapoint()
        log.debug("Produced numbers: %s" % data)
        self.emit('results', data)

    def plot_live(self, *args, **kwargs):
        t=time.time()
        while self.data.empty:
            time.sleep(.1)
            if (time.time()-t)>10:
                log.warning('Timeout, no data received for liveplot')
        self.plot(*args, **kwargs)
        while not self.should_stop():
            self.plot(*args, **kwargs)
        if self.is_alive():
            self.terminate()

    def plot(self, *args, **kwargs):
        if not self.plots:
            kwargs['title'] = self.title
            ax = self.data.plot(*args, **kwargs)
            self.plots.append({'type': 'plot', 'args': args, 'kwargs': kwargs, 'ax': ax})
            if ax.get_figure() not in self.figs:
                self.figs.append(ax.get_figure())
            self._user_interrupt = False
        else:
            self.update_plot()

    def clear_plot(self):
        for fig in self.figs:
            fig.clf()
            pl.close()
        self.figs = []
        self.plots = []
        gc.collect()

    def update_plot(self):
        from IPython import display
        try:
            tasks = []
            self.data
            for plot in self.plots:
                ax = plot['ax']
                if plot['type']=='plot':
                    x,y = plot['args'][0], plot['args'][1]
                    if type(y) == str:
                        y = [y]
                    for yname,line in zip(y,ax.lines):
                        self.update_line(ax, line, x, yname)
                if plot['type']=='pcolor':
                    x,y,z = plot['x'], plot['y'], plot['z']
                    update_pcolor(ax, x, y, z)
            
            display.clear_output(wait=True)
            display.display(*self.figs)
            time.sleep(0.1)
        except KeyboardInterrupt:
            display.clear_output(wait=True)
            display.display(*self.figs)
            self._user_interrupt = True
    
    def pcolor(self, xname, yname, zname, *args, **kwargs):
        title = self.title
        x,y,z = self._data[xname], self._data[yname], self._data[zname]
        shape = (len(y.unique()), len(x.unique()))
        diff = shape[0]*shape[1] - len(z)
        Z = np.concatenate((z.values, np.zeros(diff))).reshape(shape)
        df = pd.DataFrame(Z, index=y.unique(), columns=x.unique())
        ax = sns.heatmap(df)
        pl.title(title)
        pl.xlabel(xname)
        pl.ylabel(yname)
        ax.invert_yaxis()
        pl.plt.show()
        self.plots.append({'type': 'pcolor', 'x':xname, 'y':yname, 'z':zname, 'args':args, 'kwargs':kwargs, 'ax':ax})
        if ax.get_figure() not in self.figs:
            self.figs.append(ax.get_figure())
    
    def update_pcolor(self, ax, xname, yname, zname):
        x,y,z = self._data[xname], self._data[yname], self._data[zname]
        shape = (len(y.unique()), len(x.unique()))
        diff = shape[0]*shape[1] - len(z)
        Z = np.concatenate((z.values, np.zeros(diff))).reshape(shape)
        df = pd.DataFrame(Z, index=y.unique(), columns=x.unique())
        cbar_ax = ax.get_figure().axes[1]
        sns.heatmap(df, ax=ax, cbar_ax=cbar_ax)
        ax.set_xlabel(xname)
        ax.set_ylabel(yname)
        ax.invert_yaxis()

    def update_line(self, ax, hl, xname, yname):
        del hl._xorig, hl._yorig
        hl.set_xdata(self._data[xname])
        hl.set_ydata(self._data[yname])
        ax.relim()
        ax.autoscale()
        gc.collect()