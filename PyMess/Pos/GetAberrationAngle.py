from .. import Globals
from .GetMercurySpeed import GetMercurySpeed
import numpy as np

def GetAberrationAngle(Date=None,Vsw=440.0):
	'''
	Returns the aberration angle of the mangetosphere.
	
	Inputs:
		Date: Optional, if set to None, then all dates are calculated
			and returned, if set to a single scalar integer with the 
			format yyyymmdd, then the aberration angle for that date is
			returned.
		Vsw: Solar wind velocity in km/s
		
	Returns:
		numpy.recarray object
	
	'''
	if not Vsw in Globals.AberrationAngle.keys():
		dtype = [('Date','int32'),('Angle','float32')]
		
		tmp  = GetMercurySpeed()
		data = np.recarray(tmp.size,dtype=dtype)
		data.Date = tmp.Date
		data.Angle = np.arctan2(tmp.v,Vsw)*180.0/np.pi
		Globals.AberrationAngle[Vsw] = data
		
	if Date is None:
		return Globals.AberrationAngle[Vsw]
	else:
		tmp = Globals.AberrationAngle[Vsw]
		use = np.where(tmp.Date == Date)[0]
		return tmp[use[0]]
		
		
