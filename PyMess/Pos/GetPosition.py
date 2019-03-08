from .. import Globals
from ._ReadPosition import _ReadPosition
import numpy as np

def GetPosition(Date=None):
	'''
	Returns the position of MESSENGER around Mercury in MSM (Mercury-
	centric solar magnetospheric) coordinates. 
	
	Inputs:
		Date: Optional- Set to None to return positions for the entire 
			mission; set to a scalar date with the format yyyymmdd to
			return the positions of MESSENGER throughout one day; set to
			a two-element list, tuple or array to look for positions
			within a date range.
			
	Returns:
		numpy.recarray
			
	'''
	
	#firstly, check if the data are loaded
	if Globals.Position is None:
		Globals.Position = _ReadPosition()
		
	if Date is None:
		return Globals.Position
	elif np.size(Date) == 2:
		use = np.where((Globals.Position.Date >= Date[0]) & (Globals.Position.Date <= Date[1]))[0]
		return Globals.Position[use]
	else:
		use = np.where(Globals.Position.Date == Date)[0]
		return Globals.Position[use]
