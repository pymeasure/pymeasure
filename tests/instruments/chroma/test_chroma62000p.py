from pymeasure.instruments.chroma.chroma62000p import Chroma62024P6008
from time import sleep

@pytest.mark.skip(reason="no way of currently testing this just in SW")
def test_Chroma_current_limit_turn_on_and_off():
    psu=Chroma62024P6008('USB0::0x1698::0x0837::007000000446::0::INSTR')
    print(psu.id)
    psu.output_current_limit = 1
    psu.output_voltage_level = 5
    psu.output_enable()
    sleep(2)
    print(psu.output_voltage)
    psu.output_disable()

