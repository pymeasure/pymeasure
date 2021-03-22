from pymeasure.instruments.signalrecovery import DSP7265

if __name__ == '__main__':
    li = DSP7265("visa://phys8173.campus.tue.nl/GPIB0::11::INSTR")
    print(li.curve_buffer_length)
