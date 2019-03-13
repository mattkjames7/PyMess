from ._ReadSolarWindTimes import _ReadSolarWindTimes
from .. import Globals

def GetSolarWindTimes():
	'''	
	Retrieves the list of times when MESSENGER was within the solar wind
	from file or from memory.
	
	Returns:
		numpy.recarray
	'''	
	if Globals.SWTimes is None:
		Globals.SWTimes = _ReadSolarWindTimes()
	
	return Globals.SWTimes
