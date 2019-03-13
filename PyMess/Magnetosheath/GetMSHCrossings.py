from .. import Globals
from ._ReadMSHCrossings import _ReadMSHCrossings


def GetMSHCrossings():
	
	if Globals.MSHTimes is None:
		Globals.MSHTimes = _ReadMSHCrossings()
	
	return Globals.MSHTimes
