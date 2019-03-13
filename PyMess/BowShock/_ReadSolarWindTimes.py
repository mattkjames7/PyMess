from .. import Globals
import PyFileIO as pf


def _ReadSolarWindTimes():
	'''	
	Reads the list of times when MESSENGER was within the solar wind.
	'''
	fname = Globals.ModulePath+'__data/BS/SWTimes.dat'
	dtype=[('Date0','int32'),('ut0','float32'),('Date1','int32'),('ut1','float32'),('Dt','float32')]
	
	return pf.ReadASCIIData(fname,Header=False,dtype=dtype)
