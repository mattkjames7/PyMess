import numpy as np
import os
import PyFileIO as pf

def _ReadTraceFootprints(Date,Scaled=True):
	'''
	This function will read the magnetic field traces made using the
	KT17 magnetic field model (Korth et al., 2017) for every minute on
	the provided date.
	
	Inputs:
		Date: 32-bit integer with the date in the format yyyymmdd.
		Scaled: Boolean, if True then a trace will be returned where the
			magnetosphere was scaled by the distance of Mercury from the
			Sun. If False, it will return the trace of the average 
			magnetic field model.
			
	Returns:
		numpy.recarray with the field line footprints on the planetary
		surface, the surface of invariant latitude, and the magnetic
		equatorial plane.
	'''
	
	path = os.getenv('MESSENGER_PATH')+'/'+'KT17Traces/'
	if Scaled:
		path += 'MessengerRScaled/'
	else:
		path += 'MessengerDefault/'
		
	fname = path+'{:08d}.bin'.format(Date)
	dtype=[('Date','int32'),('ut','float32'),('mlatn','float32'),('mlats','float32'),
			('latn','float32'),('lats','float32'),('mltn','float32'),('mlts','float32'),
			('lctn','float32'),('lcts','float32'),('mlte','float32'),('lshell','float32'),
			('fl_len','float32'),('xmsm','float32'),('ymsm','float32'),('zmsm','float32'),
			('bx','float32'),('by','float32'),('bz','float32'),('Rsm','float32'),('Ab','float32'),('Rau','float32')]
			
	if not os.path.isfile(fname):
		return np.recarray(0,dtype=dtype)
			
	return pf.ReadRecarray(fname,dtype)
