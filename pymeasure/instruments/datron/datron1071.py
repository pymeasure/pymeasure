#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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


from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, strict_range
from pyvisa.errors import VisaIOError


class datron1071(Instrument):
    """
    Represent the Datron 1071 high resulution DMM up to 7.5 digit, old but stable DMM
    Unit has no own SCPI commandos. 

    Implemented: more as BASIC, useful

    Commandos:
    avarage(True / False)   Avarage mode
    filter(True / False)    Filter mode
    set_b(val)              set B register
    set_c(val)              set C register
    set_high(val)           set high limit register
    set_low(val)            set low limit register
    front()                 set Front Terminal (read Manual!)
    rear()                  set Rear Terminal (read Manual!)
    inp_zero()              Input Zero, use low EMF short
    self_tst()              Self Test, no connection. todo Error handling
    ratio_off()             ratio modus off, normal mode
    ratio_1trig()           ratio modus on, one trigger to measure (read Manual!)
    ratio_1trig()           ratio modus on, two trigger to measure (read Manual!)
    mode_ohm()              set measurement mode ohm
    mode_acv()              set measurement mode AC Voltage
    mode_dcv()              set measurement mode DC Voltage
    mode_aci()              set measurement mode AC Current
    mode_dci()              set measurement mode DC Current
    mode_dcacv()            set measurement mode AC Voltage coppling DC
    mode_dcaci()            set measurement mode AC Current coppling DC
    cal_enable()            enable CALIBRATION MODE (read Manual!)
    cal_diable(self)        diable CALIBRATION MODE
    cal_zero()              DMM cal zero (read Manual!)
    cal_gain(opt: val)      Gain Cal of Range (read Manual!)
    cal_achf(opt: val)      Full Range HF @ AC, Cal of Range (read Manual!)
    cal_lin()               Lin cal, 1 Mohm Source spezial tool (read Manual!)
    cal_ib()                Ib cal Bias, 10 Mohm Source spezial tool (read Manual!)
    write_raw(val)          send raw data strint to DMM, 'R4F3' DCV, Range 1 V
    rangemode(mode)         range R0 - R7, auto
    minmax_cls()            clear min max store
    mode_max()              max modus
    mode_min()              min modus
    mode_maxmin()           max-min modus
    mode_maxmin_off()       max min modus off, normal mode
    triggermode(mode)       T0 - T7, int, ext, SW
    trigger()               SW trigger
    readval(loops=10,trg = False) Returns a List [0]Value, [1]Unit, 
        [2]Setting 

    get_register(register)  Get Register,B, C ,HLIMIT or LLIMIT
    """
    #fake IDN, Datron1071, no internal 'IDN' command
    #program check @ Datron FW from 1981
    id = "Datron1071_FW1981"    

    ##################

        
    def __init__(self, adapter, **kwargs):
        super(datron1071, self).__init__(
            adapter, "datron1071", **kwargs
        )
        #grunddaten setzen
        #self.avarage('off')
        #self.filter('off')
        #VAL & full data
        self.write("O1=") 
        self.write_raw('R6F3M0N0P0Q0T2C1A1DXW0')

# funktion #
 

    def avarage(self,mode=False):
        """set Avarage mode
        :param mode: True or False"""  
        self.mode = mode
        if mode == False:
            self.write("A0=")
        else: 
            self.write("A1=")
###

    def set_b(self,valb = 0):
        """ 
        set internal B register for Math
        :valb
        """
        self.valb = valb
        data = 'K'+str(valb)+'L1='
        self.write(data)

    def set_c(self,valc = 0):
        """ 
        set internal C register for Math
        :valc
        """
        self.valc = valc
        data = 'K'+str(valc)+'L2='
        self.write(data) 

    def set_high(self,valc = 0):
        self.valc = valc
        data = 'K'+str(valc)+'L3='
        self.write(data) 

    def set_low(self,valc = 0):
        self.valc = valc
        data = 'K'+str(valc)+'L4='
        self.write(data)                   

    def filter(self,mode=False):
        """set Filter mode
        :param mode: True or False"""  
        self.mode = mode
        if mode == False:
            self.write("C0=")
        else: 
            self.write("C1=")

    def front(self):
        """
        Set DMM to front Terminal        
        """
        self.write("I0=")        

    def rear(self):
        """
        Set DMM to Rear Terminal (option). Switch on backside set to
        position Rear.
        """
        self.write("I1=")

    def inp_zero(self):
        """
        Input Zero, use low EMF short
        """
        self.write("Z=")

    def self_tst(self):
        """
        Self Test, no connection
        todo Error handling
        """
        self.write("Y=")

# ratio #

    def ratio_off(self):
        """
        ratio modus off (normal mode)
        """        
        self.write("P0=") 

    def ratio_1trig(self):
        """
        ratio modus on, one trigger to measure
        """  
        self.write("P1=") 

    def ratio_2trig(self):
        """
        ratio modus on, two trigger to measure    
        """    
        self.write("P2=") 
    

# operate mode #

    def mode_ohm(self):
        """
        set measurement mode ohm
        """
        self.write("F1=")   

    def mode_acv(self):
        """
        set measurement mode AC Voltage
        """
        self.write("F2=")

    def mode_dcv(self):
        """
        set measurement mode DC Voltage
        """        
        self.write("F3=")

    def mode_aci(self):
        """
        set measurement mode AC Current
        """  
        self.write("F4=")

    def mode_dci(self):
        """
        set measurement mode DC Current
        """        
        self.write("F5=")

    def mode_dcacv(self):
        """
        set measurement mode AC Voltage coppling DC 
        """         
        self.write("F6=")

    def mode_dcaci(self):
        """
        set measurement mode AC Current coppling DC 
        """         
        self.write("F7=")

# calibrate #

    def cal_enable(self):
        """
        enable CALIBRATION MODE 
        (set Cal.-Key in position 'CAL' )
        LCD lit 'CAL' after cal_enable
        """
        self.write("W1=")

    def cal_diable(self):
        """
        diable CALIBRATION MODE 
        (set Cal.-Key in position 'NORMAL' )
        """
        self.write("W0=")        

    def cal_zero(self):
        """
        DMM cal zero
        """
        self.write("G0=")

    def cal_gain(self, valcal =None ):
        """
        Gain Cal of Range
        if Nominal 'not smooth value' for exampel Standart Cell
        set the true value

        :param valcal: true value
        """
        self.valcal = valcal
        if valcal == None:
            self.write("G1=")
        else:
            data = 'K'+str(valcal)+'G1='
            self.write(data)


    def cal_achf(self,valcal =None):
        """
        Full Range HF @ AC, Cal of Range
        if Nominal 'not smooth value' 
        set the true value

        :param valcal: true value
        """
        self.valcal = valcal
        if valcal == None:
            self.write("G3=")
        else:
            data = 'K'+str(valcal)+'G3='
            self.write(data)

    def cal_lin(self):
        """
        Lin cal (1 Mohm Source spezial tool)
        """
        self.write("G4=")

    def cal_ib(self):
        """
        Ib cal Bias (10 Mohm Source spezial tool)
        """        
        self.write("G2=")


########
    def write_raw(self,raw=""):
        """
        send raw data string to DMM
        for example 'R4F3' DCV, Range 1 V

        :param raw: raw data string 
       """
        self.raw = raw
        if raw != "":
            raw = raw.upper()
            raw= raw +'='
            self.write(raw)


# set DMM Range

    def rangemode(self,mode = 'AUTO'):
        """
        set DMM range

        :param auto or R0 auto range
        :param R1 to R7 fix range
        R1 10 ohm, 100 mV, µA
        R2 100 mV, µA, ohm
        R3 1 V, mA, kohm
        R4 10 V, mA, kohm
        R5 100 V, mA, kohm
        R6 1000 V, mA, kohm
        R7 10 Mohm, 1000 V, mA
        """
        self.mode = mode 
        mode = mode.upper()
        mode = mode.replace('AUTO','R0')
        mode = mode +'='
        self.write(mode)

# min max #

    def minmax_cls(self):
        """
        clear min max store 
        """
        self.write("L0=")

    def mode_max(self):
        """
        max modus 
        """
        self.write("N1=")

    def mode_min(self):
        """
        min modus 
        """        
        self.write("N2=")

    def mode_maxmin(self):
        """
        max-min modus 
        """        
        self.write("N3=")

    def mode_maxmin_off(self):
        """
        max min modus off (normal mode) 
        """
        self.write("N0=")        


# trigger #

    def triggermode(self,mode = 'INT'):
        """
        trigger mode for DMM

        :parameter :mode INT, T0 intern
        EXT, T1 Externer Trigger
        SW, T2 SW Trigger (@)
        T3, SW or exter
        T4, Manual (front Panel)
        T5, Extern or manual
        T6, SW or manuel
        T7, sw or extern or manal
        """

        self.mode = mode 
        mode = mode.upper()
        mode = mode.replace('INT','T0')
        mode = mode.replace('EXT','T1')
        mode = mode.replace('SW','T2')
        mode = mode +'='
        self.write(mode)
  

    def trigger(self):
        """
        send SW Trigger to DMM (@)
        """
        self.write("@")

# reading val from dmm #

    def readval(self,loops=10,trg = False):
        """ Returns a List [0]Value, [1]Unit, 
        [2]Setting 
        :param loops: Loops for waiting no Error, after loops with
                        error, return Error
        :param trg: True or False, True send SW (@) Trigger"""
        self.loops = loops
        self.trg = trg
        n=1
        while n !=loops:
            if trg == True:
                self.write("@")
            lesen = self.read()
            if (',R' in lesen) and (lesen.count(",R")==1):
                lesen = lesen.strip()
                lesen = lesen.replace('ERROR OL','ERROR OL,ERROR OL',1)

                if 'ERROR 4' in lesen:
                    lesen = lesen.replace('ERROR 4','ERROR 4,ERROR 4',1)
                lesen = lesen.replace('PU,R',',%,R',1)
                lesen = lesen.replace('O,R',',Ohm,R',1)    

                if '#' in lesen:
                    lesen = lesen.replace('#','')
                    lesen = lesen.replace('V,R',',Vacdc,R',1)
                    lesen = lesen.replace('A,R',',Aacdc,R',1)

                if ('+' in lesen) or ('-' in lesen):
                    lesen = lesen.replace('V,R',',Vdc,R',1)
                    lesen = lesen.replace('A,R',',Adc,R',1)

                if '~' in lesen:
                    lesen = lesen.replace('~','')
                    lesen = lesen.replace('V,R',',Vac,R',1)
                    lesen = lesen.replace('A,R',',Aac,R',1) 

                #print (n,': wert',lesen,'###')
                n = loops-1
            else:
                #print ('not yet')
                lesen = "ERROR,ERROR,ERROR"
                #n = n -1
            n = n+1
        lesen = lesen.split(',')

        return lesen 

# read register for math and limits # 

    def get_register(self,register=None):
        """ Get Register
        :param register: B, C ,HLIMIT or LLIMIT 
        """
        self.register = register
        register = register.strip()
        register = register.upper()
        if register == 'B':
            state = self.ask("V1=")
            state = state.replace('L1',',B',1)
        elif register == 'C':
            state = self.ask("V2=")
            state = state.replace('L2',',C',1)
        elif register == 'HLIMIT':
            state = self.ask("V3=")
            state = state.replace('L3',',high Limit',1)
            state = state.replace('ERROR 2','ERROR 2,L3',1)
        elif register == 'LLIMIT':
            state = self.ask("V4=")   
            state = state.replace('L4',',low Limit',1)
            state = state.replace('ERROR 2','ERROR 2,L2',1)
        else:
            state = None 
        state = state.split(',')    
        return state










