import PyFileIO as pf
from .. import Globals

def _ReadMercurySpeed():
	'''
	Reads the file which stored Mercury's orbital speed from 20080101
	to 20150431.
	'''
	
	fname = Globals.ModulePath +'/__data/MercurySpeed.dat'
	data = pf.ReadASCIIData(fname,True,dtype=[('Date','int32'),('v','float32')])
	
	return data
