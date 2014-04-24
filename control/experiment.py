from pyqtgraph.Qt import QtCore
from PyQt4 import QtGui, uic
from parameter import Parameter
import numpy as np

class Experiment(QtCore.QThread):
	"""This is the base class for running actual experiments. We must define
	init(), exit(), and run() below, making sure to retain the structure and 
	signaling of the run() function. All other behaviors should be taken care
	of automatically, including automatic shutdown in the case of thread 
	termination or the window being closed, etc. Data storage here is 
	ephemeral --- only the most recent values are stored, and it is left to
	the plotting and logging classes to ensure persistance."""
	
	# Signals must be defined here
	newData       = QtCore.pyqtSignal()
	newTrace      = QtCore.pyqtSignal()
	newLog        = QtCore.pyqtSignal(str)
	aborted       = QtCore.pyqtSignal()
	finishedTrace = QtCore.pyqtSignal()

	def __init__(self, parent=None):
		super(Experiment, self).__init__()

		# Thread control
		self.exiting           = False 
		self.shutdownCompleted = False
		
		self.data        = []
		self.instruments = []
	
	def initParameters(self, params):
		"""Establish the parameters for a measurement run"""
		self.params = params
	def initInstruments(self):
		"""Bring instrumentation online"""
		pass

	def getData(self):
		return self.data
	
	# Terminating the measurement thread
	def __del__(self):
		self.exiting = True
		self.wait()
	def stop(self):
		self.__del__()
	def exit(self):
		# Should be called in the event of an intentional or inadvertant shutdown
		self.exiting = True
		if not self.shuttingDownInstruments:
			# Prevent this from somehow being called twice...
			self.shuttingDownInstruments = True
			self.newLog.emit("<b>Shutting Down Measurement</b>")
			for instr in self.instruments:
				instr.shutdown()
			self.newLog.emit("Done shutting down")

	# Running the actual measurement
	def run(self):
		"""Perform the measurement"""
		try:
			self.exiting = False
			print "Running!"
			self.init()
			i = 0
			while not self.exiting and i < 5:
				num = np.random.random()
				self.latestData = [num, num**2]
				self.data.append([num, num**2])
				self.newData.emit()
				time.sleep(0.2)
				i += 1
		except Exception, ex:
			logging.exception("Exception occured in measurement loop")
		self.finished.emit()
		self.exit()
		return

class ExperimentGUI(QtGui.QMainWindow):
	"""This is the main window of the experiment. We pass it a subclass of Experiment
	that will be run/stopped as desired from this window."""
	def __init__(self, name, uiForm, parent=None):		
		super(ExperimentGUI, self).__init__()

		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		# Load the UI file
		self.ui = uic.loadUi(uiForm, self)
		self.setWindowTitle(name)
		# For logging
		self.log = ''

		# Load the previous user settings
		self.settings = QtCore.QSettings("Cornell University", name)
		self.runningExperiment = False

	def closeEvent(self, ce):
		self.fileQuit()

	def fileQuit(self):
		if self.runningExperiment:
			self.expThread.stop()
			self.runningExperiment = False 
		self.close()

	def settingsDict(self, parent, unitMappings=None):
		"""Packs current settings into a dictionary for objects that are children of
		the specified object. UnitMappings is a dictionary containing multiplicative
		factors to be multiplied by the values found in the actual input fields.

		e.g. a QDoubleSpinBox called currentmA would warrent
		unitMappings = {'currentmA': 1.0e-3}
		"""
		getters = {QtGui.QCheckBox:      "isChecked",
				   QtGui.QComboBox:      "currentText",
				   QtGui.QDoubleSpinBox: "value",
				   QtGui.QSpinBox:       "value",
				   QtGui.QLineEdit:      "text",
				   QtGui.QRadioButton:   "isChecked",
				   Parameter:            "value",}

		d = {}
		for fieldType, method in getters.iteritems():
			for child in parent.findChildren(fieldType, QtCore.QRegExp("^(?!qt_spinbox_lineedit).*$")):
				value = getattr(child, method)()
				cname = str(child.objectName())
				if isinstance(value, QtCore.QString):
					value = str(value)
				if unitMappings is not None and (cname in unitMappings):
					d[cname] = value*unitMappings[cname]
				if isinstance(child, Parameter):
					# Also store the unit since it's available
					d[cname+"Unit"] = child.getUnit()
					d[cname] = value
				else:
					d[cname] = value
		return d

	def storeSettings(self):
		"""Saves the values in the interface using qsettings"""
		getters = {QtGui.QCheckBox:      ("QCheckBox", "isChecked", bool),
				   QtGui.QComboBox:      ("QComboBox", "currentIndex", int),
				   QtGui.QDoubleSpinBox: ("QDoubleSpinBox", "value", float),
				   QtGui.QSpinBox:       ("QSpinBox", "value", int),
				   QtGui.QLineEdit:      ("QLineEdit", "text", str),
				   QtGui.QRadioButton:   ("QRadioButton", "isChecked", bool),
				   Parameter:            ("Parameter", "value", float),}

		for fieldType, info in getters.iteritems():
			for child in self.ui.findChildren(fieldType, QtCore.QRegExp("^(?!qt_spinbox_lineedit).*$")):
				self.settings.setValue(info[0]+"/"+child.objectName(), getattr(child, info[1])())

	def loadSettings(self):
		"""Restored saved settings using qsettings"""
		setters = {QtGui.QCheckBox:      ("QCheckBox", "setChecked", "toBool"),
				   QtGui.QComboBox:      ("QComboBox", "setCurrentIndex", "toInt"),
				   QtGui.QDoubleSpinBox: ("QDoubleSpinbox", "setValue", "toFloat"),
				   QtGui.QSpinBox:       ("QSpinBox", "setValue", "toInt"),
				   QtGui.QLineEdit:      ("QLineEdit", "setText", "toString"),
				   QtGui.QRadioButton:   ("QRadioButton", "setChecked", "toBool"),
				   Parameter:            ("Parameter", "setValue", "toFloat"),}

		for fieldType, info in setters.iteritems():
			self.settings.beginGroup(info[0])
			for key in self.settings.childKeys():
				value = getattr(self.settings.value(key), info[2])()
				if isinstance(value, tuple):
					value = value[0]
				getattr(self.ui.findChildren(fieldType, key)[0], info[1])(value)
			self.settings.endGroup()