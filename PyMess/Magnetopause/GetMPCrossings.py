from .. import Globals
from ._ReadMPCrossings import _ReadMPCrossings
import numpy as np

def GetMPCrossings(Date=None):
	'''
	Retrieves the MP crossings list either from memory or file.
	
	Input:
		Date: 32-bit integer scalar or 2 element array, list or tuple in
			the format yyyymmdd to select crossings from a specific date
			range, or None to return all crossings.
			
	Returns:
		numpy.recarray
	'''
	if Globals.MPData is None:
		Globals.MPData = _ReadMPCrossings()
		
	if not Date is None:
		#date or date range specified but not ut
		if np.size(Date) == 1:
			use = np.where((Globals.MPData.Date0 == Date) | 
						(Globals.MPData.Date1 == Date))[0]
		else:
			use = np.where((Globals.MPData.Date0 <= Date[1]) & 
						(Globals.MPData.Date1 >= Date[0]))[0]
		return Globals.MPData[use]
	else:
		return Globals.MPData
