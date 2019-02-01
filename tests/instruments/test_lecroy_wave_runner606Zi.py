from pymeasure.instruments.lecroy.waverunner606zi import WaveRunner606Zi
from pymeasure.adapters.activedso import ActiveDSOAdapter

DEFAULT_TIMEOUT = 1
scope_address = '146.136.35.208'

scope = WaveRunner606Zi(address=scope_address)
print(scope.id)
print(scope.measurement.top('C2'))
print(scope.measurement.rms('C2'))
print(scope.measurement.rms('C3'))
print(scope.measurement.peak2peak('C3'))
print(scope.measurement.mean('C3'))
print(scope.get_measurement_Px(7))

filename = "D:\\Setups\\190123_DSOSetupOpenLoop.lss"
scope.recall_setup_from_file(filename)

scope.disconnect()