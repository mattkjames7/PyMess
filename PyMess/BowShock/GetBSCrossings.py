from .. import Globals
from ._ReadBSCrossings import _ReadBSCrossings
import numpy as np

def GetBSCrossings(Date=None):
	'''
	Retrieves the BS crossings list either from memory or file.
	
	Input:
		Date: 32-bit integer scalar or 2 element array, list or tuple in
			the format yyyymmdd to select crossings from a specific date
			range, or None to return all crossings.
			
	Returns:
		numpy.recarray
	'''
	if Globals.BSData is None:
		Globals.BSData = _ReadBSCrossings()
		
	if not Date is None:
		#date or date range specified but not ut
		if np.size(Date) == 1:
			use = np.where((Globals.BSData.Date0 == Date) | 
						(Globals.BSData.Date1 == Date))[0]
		else:
			use = np.where((Globals.BSData.Date0 <= Date[1]) & 
						(Globals.BSData.Date1 >= Date[0]))[0]
		return Globals.BSData[use]
	else:
		return Globals.BSData
