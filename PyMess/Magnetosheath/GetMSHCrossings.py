from .. import Globals
from ._ReadMSHCrossings import _ReadMSHCrossings


def GetMSHCrossings():
	
	if Globals.MSHTimes is None:
		Globals.MSHTimes = _ReadMSHCrossings()
	
	if not Date is None:
		#date or date range specified but not ut
		if np.size(Date) == 1:
			use = np.where((Globals.MSHTimes.Date0 == Date) | 
						(Globals.MSHTimes.Date1 == Date))[0]
		else:
			use = np.where((Globals.MSHTimes.Date0 <= Date[1]) & 
						(Globals.MSHTimes.Date1 >= Date[0]))[0]
		return Globals.MSHTimes[use]
	else:
		return Globals.MSHTimes
