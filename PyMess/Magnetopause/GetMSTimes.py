import numpy as np
from .. import Globals
from ._ReadMSTimes import _ReadMSTimes

def GetMSTimes(Date=None):
	
	if Globals.MSTimes is None:
		Globals.MSTimes = _ReadMSTimes()
		
	if not Date is None:
		#date or date range specified but not ut
		if np.size(Date) == 1:
			use = np.where((Globals.MSTimes.Date0 == Date) | 
						(Globals.MSTimes.Date1 == Date))[0]
		else:
			use = np.where((Globals.MSTimes.Date0 <= Date[1]) & 
						(Globals.MSTimes.Date1 >= Date[0]))[0]
		return Globals.MSTimes[use]
	else:
		return Globals.MSTimes
