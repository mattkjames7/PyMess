from .. import Globals
from ._ReadOrbits import _ReadOrbits

def GetOrbits():
	'''
	Returns the start and end dates and times of each orbit of MESSENGER 
	around Mercury.
	
	'''
	
	if Globals.Orbits is None:
		Globals.Orbits = _ReadOrbits()
		
	return Globals.Orbits
