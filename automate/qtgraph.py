import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

class FiniteDataPlot(pg.PlotItem):
    """ Represents a 2D line plot with optional errorbars
    based on a finite number of data points that is known upon
    construction. Mediates passing data to the plotting backend
    as the update method is called with a dictionary that has the labels
    defined for x and y on construction.   
    """
    
    sigDataUpdated = QtCore.Signal(object)
    
    def __init__(self, count, x, y, **labels):
        """ Sets up the plot for a certain amount of data (count), given
        labels x, y, and optional arguments xerr and yerr which correspond
        to how the data is named in a dictionary to be passed into update
        """
        self.curve = None
        self.errorBars = None
        self._ptr = 0
        self._plotSettings = {}
        
        self._map = {'x': x, 'y': y}
        if 'xerr' in labels:
            self._map['xerr'] = labels['xerr']
        if 'yerr' in labels:
            self._map['yerr'] = labels['yerr']
        self._data = np.empty(count, dtype=[(label, '<f8') for label in self._map])
        super(FiniteDataPlot, self).__init__()
    
    def setPlot(self, **kwargs):
        """ Sets the keyword arguments for the plot settings """
        self._plotSettings = kwargs
        
    def update(self, data):
        """ Appends the data from the dictionary, based on the labels specified
        during construction, to the plot curve and the error bars and emits
        the sigDataUpdated signal
        """
        # Load data into numpy array
        for k, v in self._map.iteritems():
            if v in data:
                self._data[k][self._ptr] = data[v]
            else:
                raise Exception("Data field (%s) was not found in incoming data" % v)
            
        x = self._data['x'][:self._ptr+1]
        y = self._data['y'][:self._ptr+1]
        
        if self.curve == None:
            self.curve = self.plot(x=x, y=y, **self._plotSettings)
        else:
            self.curve.setData(x=x, y=y)        
        
        if 'xerr' in self._map or 'yerr' in self._map:
            top = None
            bottom = None
            left = None
            right = None
            if 'xerr' in self._map:
                top = self._data['xerr'][:self._ptr+1]
                bottom = top # Equal deviation
            if 'yerr' in self._map:
                left = self._data['yerr'][:self._ptr+1]
                right = left # Equal deviation
                
            if self.errorBars is None:
                self.errorBars = pg.ErrorBarItem(x=x, y=y, top=top, bottom=bottom, 
                                                 left=left, right=right,
                                                 beam=np.max([top, left]), 
                                                 pen=self._plotSettings.get('pen', None))
                self.addItem(self.errorBars)
            else:
                self.errorBars.setOpts(x=x, y=y, top=top, bottom=bottom, left=left, right=right)
        
        self._ptr += 1
        self.sigDataUpdated.emit(True)
        

class Crosshairs(QObject):
    
    def __init__(self, plot, pen=None):
        self.plot = plot
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pen)
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pen)
        self.plot.addItem(self.vLine, ignoreBounds=True)
        self.plot.addItem(self.hLine, ignoreBounds=True)
        
        self.label = pg.LabelItem(justify='right')
        self.position = None
        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.plot.sigDataUpdated.connect(self.update)  
    
    def update(self):
        if self.position is not None:
            if self.plot.sceneBoundingRect().contains(self.position):
                mousePoint = self.plot.vb.mapSceneToView(self.position)
                text = "<span style='color: #333333'>x = %0.3f</span>,   <span style='color: #333333'>y = %0.3f</span>"
                self.label.setText(text % (mousePoint.x(), mousePoint.y()))
                self.vLine.setPos(mousePoint.x())
                self.hLine.setPos(mousePoint.y())
    
    def mouseMoved(self, evt=None):
        if evt is not None:
            self.position = evt[0]
            self.update()
        else:
            raise Exception("Mouse location not known")
            
    def getLabel(self):
        return self.label
