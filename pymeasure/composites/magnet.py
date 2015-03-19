#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Projected field classes
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from __future__ import division, print_function
from automate.instruments import Instrument
from automate.composites import Composite
import numpy as np
import time
import os.path
import logging

class GMW_CFrame_CCMR(Composite):
    def __init__(self, cal_file_dir=None):
        super(GMW_CFrame_CCMR, self).__init__("GMW 5403 C-Frame Electromagnet - CCMR")

        # Explicit properties (internal)
        self._field_setpoint   = 0.0
        self._control_setpoint = 0.0
        self._calibrated       = False

        # Meta-programmed properties (internal with setters and getters)
        self.add_property("pause", 0.02)
        self.add_property("control_increment", 0.05)

        from automate.composites.fieldprobe import HallProbe
        from automate.instruments.keithley import Keithley2000
        from automate.instruments.yokogawa import Yokogawa7651

        self.yoko  = Yokogawa7651(2)  # Setting the field
        self.keith = Keithley2000(14) # Reading the field via Hall Probe            

        self.yoko.configSourceVoltage(10.0)
        self.max_control_value = 10.0
        self.yoko.enabled      = True
        self.keith.configMeasureVoltage(Vrange=0.1, NPLC=5.0)

        if cal_file_dir is not None:
            hall_cal_file     = os.path.join(cal_file_dir, "GMW-CFrame-CCMR-HallProbe.cal")
            control_cal_file  = os.path.join(cal_file_dir, "GMW-CFrame-CCMR-Control.cal")
            if os.path.isfile(hall_cal_file) and os.path.isfile(control_cal_file):
                self.voltageToField = np.poly1d(np.loadtxt(hall_cal_file))
                self.fieldToVoltage = np.poly1d(np.loadtxt(control_cal_file))
                self._calibrated = True
            else:
                print("Error reading calibration files.")
        else:
            print("Magnet will be used uncalibrated.")

    def get_field(self):
        if self._calibrated:
            return self.voltageToField(self.keith.voltage)
        else:
            raise Error("Attempting to read field with uncalibrated magnet.")

    def rampToControl(self, value):
        approxSteps = int(abs(value-self._control_setpoint)/self._controlIncrement)
        vals = np.linspace(self._control_setpoint, value, approxSteps+2)
        for val in vals:
            self.yoko.voltage = val
            time.sleep(self._pause)

    def rampToField(self, field):
        if (field != self._field_setpoint):
            self.rampToControl(self.fieldToVoltage(field))
            self._field_setpoint = field

    @property
    def field(self):
        return self.get_field
    @field.setter
    def field(self, value):
        self.rampToField(value)

    @property
    def control(self):
        return self._control_setpoint
    @control.setter
    def control(self, value):
        self.rampToControl(value)

    def shutdown(self):
        self.field = 0.0
        super(GMW_CFrame_CCMR, self).shutdown()

# class ProjectionFieldF20(Magnet):
#     """Projection Field magnet in F20. Everything's a damned vector."""
#     def __init__(self, coarse=False, noCalibration=False, **kwargs):

#         if 'logfunc' in kwargs:
#             self.logfunc = kwargs['logfunc']
#         else:
#             self.logfunc = print

#         self.name = "F20 Projection Field Magnet"
#         from automate.composites.fieldProbe import ThreeAxisF20
#         from automate.instruments.esp import ESP300
#         from automate.instruments.nidaqmx import DAQ
#         from automate.instruments.yokogawa import Yokogawa7651

#         self.stage = ESP300(1, logfunc = self.logfunc)       # Magnet motion control
#         self.probe = ThreeAxisF20(logfunc = self.logfunc)    # Three Axis field probe
#         self.yoko  = Yokogawa7651(7, logfunc = self.logfunc) # Setting the Kepco output
        
#         self.yoko.configSourceVoltage(10.0)
#         self.max_control_value = 10.0
#         self.stage.enabled   = True
#         self.yoko.enabled    = True

#         # These are functions for interpolation of the concentricity correction, for internal use only
#         self._xForPhi = None
#         self._yForPhi = None

#         prefix                  = "C:/ControlSuite/control/instruments/calibration/"
#         magnetCalFile           = prefix + "controls.cal"
#         thetaXZCalFile          = prefix + "thetasXZ.cal"
#         thetaYZCalFile          = prefix + "thetasYZ.cal"
#         magnitudeThetaCalFileXZ = prefix + "magnitudesThetaXZ.cal"
#         magnitudeThetaCalFileYZ = prefix + "magnitudesThetaYZ.cal"
#         concentricityCalFile    = prefix + "concentricity.cal"
#         phiCalFile              = prefix + "phis.cal"
#         magnitudePhiCalFile     = prefix + "magnitudesPhi.cal"
#         zCalFile                = prefix + "pureZ.cal"
#         yCalFile                = prefix + "pureY.cal"
#         self.zCoeffs            = [1.4265e+01,  0.0]
#         self.yCoeffs            = [-1.0394e-01, 4.8405e-01]

#         if not noCalibration:
#             self.magnetCoeffs           = np.loadtxt(magnetCalFile)
#             self.thetaXZCoeffs          = np.loadtxt(thetaXZCalFile)
#             self.thetaYZCoeffs          = np.loadtxt(thetaYZCalFile)
#             self.magnitudeThetaCoeffsXZ = np.loadtxt(magnitudeThetaCalFileXZ)
#             self.magnitudeThetaCoeffsYZ = np.loadtxt(magnitudeThetaCalFileYZ)
#             self.zCoeffs                = np.loadtxt(zCalFile)
#             self.yCoeffs                = np.loadtxt(yCalFile)
#             self.setConcentricityInterpolation(concentricityCalFile)

#         super(ProjectionFieldF20, self).__init__(self.yoko.set_source_voltage, **kwargs)
#         self.setFeedbackMethod(self.probe.getField)
#         self.logfunc("Initialized <i>%s</i>." % self.name)
   
#     @property
#     def field(self):
#         return self.probe.getField()
#     @field.setter
#     def field(self, value):
#         self.rampToField(value)

#     def setConcentricityInterpolation(self, calFile):
#         """"Defines linear interpolation functions for getting the correct stage translation coordinates
#         to obtain a pure field along some in-plane angle with minimal z-component."""
#         from scipy.interpolate import interp1d
#         angles, xCorr, yCorr = np.loadtxt(calFile, unpack=True)
#         self._xForPhi = interp1d(angles, xCorr)
#         self._yForPhi = interp1d(angles, yCorr)

#     def locationForPhi(self, angle):
#         """Returns the corrected translation coordinates for applying a pure in-plane field along phi"""
#         return [float(self._xForPhi(angle)), float(self._yForPhi(angle)), angle]

#     def getField(self):
#         return self.probe.getField()

#     def getFieldAt(self, location):
#         self.stage.position = location
#         return self.probe.field
    
#     def gotoThetaXZ(self, theta):
#         xpos = self.evalPoly(theta, self.thetaXZCoeffs)
#         self.stage.position = [xpos, 0.0, 0.0]

#     def gotoThetaYZ(self, theta):
#         if (theta>=0.0) and (theta<=90.0):
#             ypos = self.evalPoly(theta, self.thetaYZCoeffs)
#             self.stage.position = [self.yCoeffs[0], self.yCoeffs[1] + ypos, self.yCoeffs[2]]
#         else:
#             self.logfunc("Cannot go to that quadrant. Blame whoever made the stage...")
#             raise Exception("Field specification error.")
    
#     def getRelativeMagnitudeXZ(self, position):
#         """Returns the field magnitude at this position relative to x=0"""
#         return self.evalPoly(position, self.magnitudeThetaCoeffsXZ)

#     def getRelativeMagnitudeYZ(self, position):
#         """Returns the field magnitude at this position relative to x=0"""
#         return self.evalPoly(position, self.magnitudeThetaCoeffsYZ)

#     def getControlValue(self, magnitude):
#         """Return the voltage that gives a pure x field of this magnitude at x=0
#         Voltages tend to be a little low, why? NOBODY KNOWS!!!"""
#         value = 1.012*self.evalPoly(magnitude, self.magnetCoeffs)
#         if abs(value) > self.max_control_value:
#             value = self.max_control_value*np.sign(value)
#             self.logfunc("Maximum Field Reached")
#         return value

#     def getMaxFieldForTheta(self, theta):
#         """Returns the maximum field that can be applied at this polar angle (given in deg)"""
#         position = self.evalPoly(theta, self.thetaXZCoeffs)
#         return 3.45e3/self.getRelativeMagnitudeXZ(position)

#     def rampToXYfield(self, fieldX, fieldY):
#         # What's the angle from the z axis
#         phi = (180.0/np.pi)*np.arctan2(fieldY,fieldX)
#         if phi < -180.0:
#             phi = phi + 360.0
#         elif phi > 180.0:
#             phi = phi - 360.0
#         mag = np.sqrt(fieldX**2 + fieldY**2)
#         self.stage.position = self.locationForPhi(phi)
#         self.rampToControlValue(self.getControlValue(mag))

#     def rampToZfield(self, fieldZ):
#         self.stage.position = [self.zCoeffs[0], self.zCoeffs[1], 0.0]
#         magnitudeCorrection  = self.getRelativeMagnitudeXZ(self.zCoeffs[0])
#         self.rampToControlValue(self.getControlValue(fieldZ*magnitudeCorrection))

#     def rampToXfield(self, field):
#         self.stage.position = [0.0, 0.0, 0.0]
#         self.rampToControlValue(self.getControlValue(field))

#     def rampToYfield(self, fieldY):
#         self.stage.position = [self.yCoeffs[0], self.yCoeffs[1], self.yCoeffs[2]]
#         self.rampToControlValue(self.getControlValue(fieldY))

#     def rampToXZfield(self, fieldX, fieldZ):
#         # What's the angle from the z axis
#         theta = (180.0/np.pi)*np.arctan2(fieldX,fieldZ)
#         mag = np.sqrt(fieldX**2 + fieldZ**2)

#         # Calibration is good for negative control voltage (positive Hx)
#         # so we must invert the polarity here for negative Hx
#         if theta > 0.0:
#             polarity = 1.0
#         else:
#             polarity = -1.0
#             theta = 180.0 + theta

#         position             = self.evalPoly(theta, self.thetaXZCoeffs)
#         magnitudeCorrection  = self.getRelativeMagnitudeXZ(position)
        
#         if mag != 0.0:
#             self.gotoThetaXZ(theta)
#         self.rampToControlValue(self.getControlValue(polarity*mag*magnitudeCorrection))

#     def rampToYZfield(self, fieldY, fieldZ):
#         theta = (180.0/np.pi)*np.arctan2(fieldY,fieldZ)
#         mag = np.sqrt(fieldY**2 + fieldZ**2)

#         # Calibration is good for negative control voltage (positive Hx)
#         # so we must invert the polarity here for negative Hx
#         if (fieldY >=0.0) and (fieldZ >=0.0):
#             polarity = 1.0
#         elif (fieldY <=0.0) and (fieldZ <=0.0):
#             polarity = -1.0
#             theta = 180.0 + theta
#         else:
#             self.logfunc("Cannot go to that quadrant. Blame whoever made the stage...")
#             raise Exception("Field specification error.")

#         position             = self.evalPoly(theta, self.thetaYZCoeffs)
#         magnitudeCorrection  = self.getRelativeMagnitudeYZ(position)

#         if mag != 0.0: # Avoid stage tavel for theta=0 value at mag=0.0
#             self.gotoThetaYZ(theta)
#         self.rampToControlValue(self.getControlValue(polarity*mag*magnitudeCorrection))

#     def rampToField(self, field):
#         """For a vector field argument"""
#         if len(field) != 3:
#             self.logfunc("Please supply a three vector")
#             return False

#         if (sum(np.abs(field)) == 0.0):                                   # No field!
#             self.rampToControlValue(0.0)
#         elif (field[0] != 0.0 and field[1] == 0.0 and field[2] == 0.0):   # Pure X field
#             self.rampToXfield(field[0])
#         elif (field[1] != 0.0 and field[0] == 0.0 and field[2] == 0.0):   # Pure Y field
#             self.rampToYfield(field[1])
#         elif (field[2] != 0.0 and field[0] == 0.0 and field[1] == 0.0):   # Pure Z field
#             self.rampToZfield(field[2])
#         elif ((field[0] != 0.0 and field[2] != 0.0) and field[1] == 0.0): # X/Z Field, no Y
#             self.rampToXZfield(field[0], field[2])
#         elif (field[0] != 0.0 and field[1] != 0.0) and field[2] == 0.0:   # X/Y Field, no Z
#             self.rampToXYfield(field[0], field[1])
#         elif (field[1] != 0.0 or field[2] != 0.0) and field[0] == 0.0:    # Y/Z Field, no X
#             self.rampToYZfield(field[1], field[2])
#         else:
#             pass
#             self.logfunc("Cannot go to completely arbitrary field point using this method.")
#             raise Exception("Field specification error.")
    
#     def rampToThetaMag(self, theta, magnitude, plane='XZ'):
#         theta = theta*np.pi/180.0
#         if plane == "XZ":
#             self.rampToXZfield(magnitude*np.sin(theta), magnitude*np.cos(theta))
#         elif plane == "YZ":
#             self.rampToYZfield(magnitude*np.sin(theta), magnitude*np.cos(theta))
#         else:
#             self.logfunc("Invalid plane. Field specification error.")
#             raise Exception("Field specification error.")

#     def shutdown(self):
#         self.rampToField([0.0,0.0,0.0])
#         time.sleep(0.5)
#         if self.stage.enabled:
#             self.stage.home()
#         self.yoko.shutdown()
#         time.sleep(0.2)
#         self.stage.shutdown()
#         self.probe.shutdown()
#         self.logfunc("Shutting down <i>%s</i>." % self.name)

# if __name__ == '__main__':
#     magnet = cframeGMW()
#     magnet.field = 3000.0
#     print("Magnet field %f" % magnet.probe.field)
#     magnet.shutdown()
