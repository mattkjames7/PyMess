from . import Globals
from . import Pos


try:
	import KT17 as ModelField
except:
	print('KT17 module not found, to access the "ModelField" part of \
			this module, install KT17 using "pip3 install --user KT17"')
	
	def _DummyFunc(*args,**kwargs):
		print('This function does not exits, install the KT17 module')

	class _ModelField(object):
		def __init__(self,):
			self.ModelField = _DummyFunc
			self.TraceField = _DummyFunc
			self.PlotMP = _DummyFunc
			self.PlotPlanet = _DummyFunc
			self.TestTrace = _DummyFunc
			self.WithinMP = _DummyFunc

	ModelField = _ModelField()
