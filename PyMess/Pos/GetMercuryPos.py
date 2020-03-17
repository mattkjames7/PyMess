from ._ReadMercuryPos import _ReadMercuryPos
from .. import Globals
import numpy as np

def GetMercuryPos(Date=None):
	'''
	Returns a numpy.ndarray containing the position of Mercury in HCI
	coordinates for each date between 20080101 and 20150431. 
	
	'''
	if Globals.MercuryPos is None:
		Globals.MercuryPos = _ReadMercuryPos()
	
	if Date is None:		
		return Globals.MercuryPos
	else:
		use = np.where(Globals.MercuryPos.Date == Date)[0]
		return Globals.MercuryPos[use[0]]
	
