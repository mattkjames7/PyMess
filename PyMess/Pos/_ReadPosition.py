import numpy as np
import os
import PyFileIO as pf
from .. import Globals

def _ReadPosition():
	'''
	Returns the position of MESSENGER around Mercury in MSM (Mercury-
	centric solar magnetospheric) coordinates. 
	
		
	Returns:
		numpy.recarray
			
	'''

	fname = Globals.ModulePath+'__data/MessPosMSM.bin'
	dtype = [	('Date','int32'),
				('ut','float32'),
				('utc','float64'),
				('x','float32'),
				('y','float32'),
				('z','float32')]	
	if not os.path.isfile(fname):
		return np.recarray(0,dtype=dtype)
	return pf.ReadRecarray(fname,dtype)



