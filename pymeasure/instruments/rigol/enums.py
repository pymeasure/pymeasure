from enum import Enum, IntEnum
import numpy as np

class WaveformFormat(IntEnum):
    byte = BYTE = 0
    word = WORD = 1
    ascii = asc = ASCii = ASC = 2

waveformFormatMapping = [
    np.dtype("B"),
    np.dtype("H")
]

class WaveformMode(IntEnum):
    raw = RAW = 2
    normal = NORMal = norm = NORM = 0
    maximum = max = MAXimum = MAX = 1

class AcquisitionType(IntEnum):
    normal = NORMal = norm = NORM = 0
    average = AVERAGE = 2
    peak = PEAK = peakDetect = PEAKDETECT = PEAK_DETECT = 1

class DeviceMode(Enum):
    stop = STOP = "STOP"
    run = RUN = "RUN"
    single = SINGLE = "SINGLE"


class AcquisitionMode(Enum):
    realTime = rtim = rtime = RTIM = RTIMe = "RTIM"
    equalTime = etim = etime = ETIM = ETIMe = "ETIM"

class TriggerMode(Enum):
    EDGE = edge = "EDGE"
    PULSe = pulse = PULS = puls = "PULS"
    PATTern = pattern = PATT = patt = "PATT"
    ALTERNATION = "ALTERNATION"
    
    runt = RUNT = "RUNT"
    WIND = wind = "WIND"
    NEDG = nedg = "NEDG"
    SLOPe = slope = SLOP = slop = "SLOP"
    VIDeo = video = VID = vid = "VID"
    DELay = delay = DEL = "DEL"
    TIMeout = timeout = TIM = tim = "TIM"
    DURation = duration = DUR = dur = "DUR"
    SHOLd = shold = SHOL = shol = "SHOL"
    RS232 = rs232 = "RS232"
    IIC = iic = "IIC"
    SPI = spi = "SPI"

# class PulseTriggerMode(Enum):
    # +GREaterthan
    # +LESSthan
    # +EQUal
    # -GREaterthan
    # -LESSthan
    # –EQUal

class VideoTriggerMode():
    odd = oddField = ODD = ODD_FIELD = "ODD FIELD"
    even = evenField = EVEN = EVEN_FIELD = "EVEN FIELD"
    line = LINE = "LINE"
    all = allLines = ALL = ALL_LINES = "ALL LINES"


class SweepMode(Enum):
    auto = AUTO = "AUTO"
    normal = NORMal = norm = NORM = "NORM"
    single = SINGle = sing = SING = "SING"

class Coupling(Enum):
    AC = ac = "AC"
    DC = dc = "DC"
    GND = gnd = "GND"
