#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# ESP classes -- Stage controller
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from __future__ import print_function
from automate.instruments import Instrument
import time
import logging

class ESP300(Instrument):
    """This is the class for the ESP300 motion controller"""
    def __init__(self, resourceName, **kwargs):
        super(ESP300, self).__init__(resourceName, "ESP300 Stage Controller", **kwargs)

        # Dictionary for mapping axes to their numerical labels
        self.axes = {'x': 1, 'y': 2, 'phi':3}
        self.axisNames = ['x','y','phi']

        # Make sure we're in the correct units, mm here
        for axis in self.axisNames:
            self.write("%dSN2" % self.axes[axis])

        self.clearErrors()
        self.setLimits(20.0,30.0)

        # Disable x axis hardware limit... 
        self.write("1ZH100H")
        
    def clearErrors(self):
        for i in range(20):
            error = self.ask("TE?")
            if error != "0":
                logging.debug("ESP Error cleared...")
            else:
                break

    def check_errors(self):
        error = self.ask("TE?")

        axisErrors = {'00': 'MOTOR TYPE NOT DEFINED',
                    '01': 'PARAMETER OUT OF RANGE',
                    '02': 'AMPLIFIER FAULT DETECTED',
                    '03': 'FOLLOWING ERROR THRESHOLD EXCEEDED',
                    '04': 'POSITIVE HARDWARE LIMIT DETECTED',
                    '05': 'NEGATIVE HARDWARE LIMIT DETECTED',
                    '06': 'POSITIVE SOFTWARE LIMIT DETECTED',
                    '07': 'NEGATIVE SOFTWARE LIMIT DETECTED',
                    '08': 'MOTOR / STAGE NOT CONNECTED',
                    '09': 'FEEDBACK SIGNAL FAULT DETECTED',
                    '10': 'MAXIMUM VELOCITY EXCEEDED',
                    '11': 'MAXIMUM ACCELERATION EXCEEDED',
                    '12': 'Reserved for future use',
                    '13': 'MOTOR NOT ENABLED',
                    '14': 'Reserved for future use',
                    '15': 'MAXIMUM JERK EXCEEDED',
                    '16': 'MAXIMUM DAC OFFSET EXCEEDED',
                    '17': 'ESP CRITICAL SETTINGS ARE PROTECTED',
                    '18': 'ESP STAGE DEVICE ERROR',
                    '19': 'ESP STAGE DATA INVALID',
                    '20': 'HOMING ABORTED',
                    '21': 'MOTOR CURRENT NOT DEFINED',
                    '22': 'UNIDRIVE COMMUNICATIONS ERROR',
                    '23': 'UNIDRIVE NOT DETECTED',
                    '24': 'SPEED OUT OF RANGE',
                    '25': 'INVALID TRAJECTORY MASTER AXIS',
                    '26': 'PARAMETER CHARGE NOT ALLOWED',
                    '27': 'INVALID TRAJECTORY MODE FOR HOMING',
                    '28': 'INVALID ENCODER STEP RATIO',
                    '29': 'DIGITAL I/O INTERLOCK DETECTED',
                    '30': 'COMMAND NOT ALLOWED DURING HOMING',
                    '31': 'COMMAND NOT ALLOWED DUE TO GROUP',
                    '32': 'INVALID TRAJECTORY MODE FOR MOVING'}

        generalErrors = {'1': 'PCI COMMUNICATION TIME-OUT',
                    '4': 'EMERGENCY SOP ACTIVATED',
                    '6': 'COMMAND DOES NOT EXIST',
                    '7': 'PARAMETER OUT OF RANGE',
                    '8': 'CABLE INTERLOCK ERROR',
                    '9': 'AXIS NUMBER OUT OF RANGE',
                    '13': 'GROUP NUMBER MISSING',
                    '14': 'GROUP NUMBER OUT OF RANGE',
                    '15': 'GROUP NUMBER NOT ASSIGNED',
                    '17': 'GROUP AXIS OUT OF RANGE',
                    '18': 'GROUP AXIS ALREADY ASSIGNED',
                    '19': 'GROUP AXIS DUPLICATED',
                    '16': 'GROUP NUMBER ALREADY ASSIGNED',
                    '20': 'DATA ACQUISITION IS BUSY',
                    '21': 'DATA ACQUISITION SETUP ERROR',
                    '23': 'SERVO CYCLE TICK FAILURE',
                    '25': 'DOWNLOAD IN PROGRESS',
                    '26': 'STORED PROGRAM NOT STARTED',
                    '27': 'COMMAND NOT ALLOWED',
                    '29': 'GROUP PARAMETER MISSING',
                    '30': 'GROUP PARAMETER OUT OF RANGE',
                    '31': 'GROUP MAXIMUM VELOCITY EXCEEDED',
                    '32': 'GROUP MAXIMUM ACCELERATION EXCEEDED',
                    '22': 'DATA ACQUISITION NOT ENABLED',
                    '28': 'STORED PROGRAM FLASH AREA FULL',
                    '33': 'GROUP MAXIMUM DECELERATION EXCEEDED',
                    '35': 'PROGRAM NOT FOUND',
                    '37': 'AXIS NUMBER MISSING',
                    '38': 'COMMAND PARAMETER MISSING',
                    '34': 'GROUP MOVE NOT ALLOWED DURING MOTION',
                    '39': 'PROGRAM LABEL NOT FOUND',
                    '40': 'LAST COMMAND CANNOT BE REPEATED',
                    '41': 'MAX NUMBER OF LABELS PER PROGRAM EXCEEDED'}

        if error == "0":
            return 0
        if len(error) == 3:
            # Axis specific error
            axis = error[0]
            error = error[1:]
            logging.debug("ESP axis %s coughed up error %s" % (axis, axisErrors[error]))
            return error
        else:
            logging.debug("ESP coughed up error %s" % generalErrors[error])
            return error

    def setMotorStatus(self, axis, status=True):
        if not axis in self.axes:
            logging.debug("Invalid axis specified: choose either x, y, or phi")
            raise Exception("Invalid axis specification")
        if status is True:
            self.write("%dMO" % self.axes[axis])
        else:
            self.write("%dMF" % self.axes[axis])

    def getMotorStatus(self, axis):
        if not axis in self.axes:
            logging.debug("Invalid axis specified: choose either x, y, or phi")
            raise Exception("Invalid axis specification")
            return False
        else:
            return self.values("%dMO?" % self.axes[axis])==1

    def setEnabled(self, status):
        for axis in self.axes:
            self.setMotorStatus(axis, status)

    def getCoordinate(self, axis):
        if not axis in self.axes:
            logging.debug("Invalid axis specified: choose either x, y, or phi")
            raise Exception("Invalid axis specification")
        value = self.values("%dTP" % self.axes[axis])
        # The phi stage is reversed...
        if axis=='phi':
            value = -value
        return value

    def getCoordinates(self):
        coords = []
        for axis in self.axisNames:
            coords.append(self.values("%dTP" % self.axes[axis]))
        return coords

    @property
    def enabled(self):
        statuses = [self.getMotorStatus(axis) for axis in self.axes]
        return (True in statuses)
    @enabled.setter
    def enabled(self, value):
        for axis in self.axes:
            self.setMotorStatus(axis, value)

    @property
    def x(self):
        return self.getCoordinate('x')
    @x.setter
    def x(self, value):
        self.setAxis('x', value)
    @property
    def y(self):
        return self.getCoordinate('y')
    @y.setter
    def y(self, value):
        self.setAxis('y', value)
    @property
    def phi(self):
        return self.getCoordinate('phi')
    @phi.setter
    def phi(self, value):
        self.setAxis('phi', value)
    @property
    def position(self):
        return self.getCoordinates()
    @position.setter
    def position(self, value):
        self.setAxes(value)
    @property
    def location(self):
        return self.getCoordinates()
    @location.setter
    def location(self, value):
        self.setAxes(value)

    def setAxis(self, axis, value, checkFirst=True):
        # In dimensions of mm in x,y and deg in phi
        if checkFirst:
            if abs(self.getCoordinate(axis)-value) < 0.01:
                # Skip if we're already there...
                return
        if axis=='phi':
            value = -value
        self.write("%dPA%f" % (self.axes[axis], value))
        self.write("%dWS" % self.axes[axis])
        # Ensure motion is complete
        while self.values("%dMD" % self.axes[axis]) == 0:
            time.sleep(0.05)
        if (self.check_errors()!=0):
            raise Exception("Stage error raised during attempt to move.")
            return 1

    def setAxes(self, coords, checkFirst=True):
        if len(coords) == 3:
            self.setAxis('x', coords[0], checkFirst=checkFirst)
            self.setAxis('y', coords[1], checkFirst=checkFirst)
            self.setAxis('phi', coords[2], checkFirst=checkFirst)
        else:
            logging.debug("Wrong number of coordinates specified in setAxes")

    def home(self, checkFirst=False):
        self.setAxes([0.0, 0.0, 0.0], checkFirst=checkFirst)

    def zeroTranslation(self):
        self.write("%dDH" % self.axes['x'])
        self.write("%dDH" % self.axes['y'])

    def zeroPhi(self):
        self.write("%dDH" % self.axes['phi'])

    # 10mm xlimit 20mm ylimit
    def setLimits(self, xlim, ylim):
        """The supplied limits give +/- stops for either travel direction"""
        self.write("%dSL%f" % (self.axes['x'], -xlim))
        self.write("%dSR%f" % (self.axes['x'], +xlim))
        self.write("%dSL%f" % (self.axes['y'], -ylim))
        self.write("%dSR%f" % (self.axes['y'], +ylim))

    def shutdown(self):
        self.setEnabled(False)
        super(ESP300, self).shutdown()

