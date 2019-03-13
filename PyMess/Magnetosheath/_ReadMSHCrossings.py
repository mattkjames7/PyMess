import PyFileIO as pf
from .. import Globals

def _ReadMSHCrossings():
	'''
	Reads the file contining the list of crossings of MESSENGER through
	the magnetosheath.
	
	Returns:
		numpy.recarray
	'''
	fname = Globals.ModulePath+'__data/MSHCrossings.dat'
		
	dtype = [('Date0','int32'),('ut0','float32'),('Date1','int32'),('ut1','float32'),('dir','U1')]
	return pf.ReadASCIIData(fname,Header=False,dtype=dtype)
