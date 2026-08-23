import numpy as np
import os
import PyFileIO as pf
import DateTimeTools as TT
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
				('unix','float64'),
				('x','float32'),
				('y','float32'),
				('z','float32')]	
	if not os.path.isfile(fname):
		return np.recarray(0,dtype=dtype)
	data = pf.ReadRecarray(fname,dtype)
	data.unix = TT.UnixTime(data.Date,data.ut)
	return data


