from ._ReadMercurySpeed import _ReadMercurySpeed
from .. import Globals

def GetMercurySpeed():
	'''
	Returns a numpy.ndarray containing the speed of Mercury for each 
	date between 20080101 and 20150431. 
	
	'''
	if Globals.MercurySpeed is None:
		Globals.MercurySpeed = _ReadMercurySpeed()
		
	return Globals.MercurySpeed
	
	
