from ._ReadTraceFootprints import _ReadTraceFootprints
from .. import Globals

def GetTraceFootprints(Date,Scaled=True,MaxLoaded=None):
	'''
	This function will get the magnetic field traces made using the
	KT17 magnetic field model (Korth et al., 2017) for every minute on
	the provided date.
	
	Inputs:
		Date: 32-bit integer with the date in the format yyyymmdd.
		Scaled: Boolean, if True then a trace will be returned where the
			magnetosphere was scaled by the distance of Mercury from the
			Sun. If False, it will return the trace of the average 
			magnetic field model.
		MaxLoaded: Limits the total number of days stored in RAM, the 
			full set of both scaled and average traces takes up about
			380MB on disk, so this shouldn't be necessary really.
			
	Returns:
		numpy.recarray with the field line footprints on the planetary
		surface, the surface of invariant latitude, and the magnetic
		equatorial plane.
	'''

	
	#get dict key
	key = '{:08d}'.format(Date)
	if Scaled:
		key += '-scaled'
	
	#check if the key already exists
	keys = list(Globals.Traces.keys())
	if key in keys:
		out = Globals.Traces[key]
	else:
		#check if there are too many days of traces loaded
		if not MaxLoaded is None:
			dkey =  len(keys) - (MaxLoaded-1)
			if dkey > 0:
				for i in range(0,dkey):
					Globals.Traces.pop(keys[i])
		
		#load new key
		Globals.Traces[key] = _ReadTraceFootprints(Date,Scaled)
		out = Globals.Traces[key]
		
	return out
		
				
		
	
