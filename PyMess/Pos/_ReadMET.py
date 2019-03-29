from .. import Globals
import PyFileIO as pf

def _ReadMET():
	'''
	Reads a data file containing the mission elapsed times (METs) at the 
	start of every date from 20080101 - 20150430.

	Returns:
		numpy.recarray
	
	'''
	fname = Globals.ModulePath + '__data/MessengerMET.dat'
	dtype = [('Date','int32'),('ut','float32'),('MET','float64')]
	data = pf.ReadASCIIData(fname,dtype=dtype)
	
	return data
