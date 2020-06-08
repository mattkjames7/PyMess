from .. import Globals
from ._ReadResList import _ReadResList

def GetResList():
	'''
	This function should return a numpy.recarray which lists the 
	approximate time resolutions of the MAG data between Date0,ut0 and
	Date1,ut1.
	'''
	if Globals.MagRes is None:
		Globals.MagRes = _ReadResList()
	
	return Globals.MagRes 
