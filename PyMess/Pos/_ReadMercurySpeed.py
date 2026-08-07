import PyFileIO as pf
from .. import Globals
import DateTimeTools as TT
import numpy as np

def _ReadMercurySpeed():
	'''
	Reads the file which stored Mercury's orbital speed from 20080101
	to 20150431.
	'''
	
	fname = Globals.ModulePath +'/__data/MercurySpeed.dat'
	data = pf.ReadASCIIData(fname,Header=True,dtype=[('Date','int32'),('unix','float64'),('v','float32')])
	data.unix = TT.UnixTime(data.Date,np.zeros(data.size))
	
	return data
