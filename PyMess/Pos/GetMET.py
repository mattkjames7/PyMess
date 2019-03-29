from ._ReadMET import ReadMET
import numpy as np
from .. import Globals
import DateTimeTools as TT
from scipy.interpolate import interp1d

def GetMET(Date=None,ut=None):
	'''
	Retrieves METs either from file or memory if they are already loaded.
	
	Inputs:
		Date: None, integer or array of integers in the format yyyymmdd.
		ut: None or an array of floating point times (in hours from the
			start of the day) the same size as Date.
			
		**NOTE**
		When Date == None and ut == None:
			all METs are returned
		
		When Date is a single integer (ut is None):
			MET for the start of that day is returned
		
		When Date is two integers (ut is None):
			METs for the range of dates between Date[0] and Date[1] are
			returned
			
		When Date and ut are both arrays:
			returns an interpolated array of MET
	'''
	#load into memory if not already there
	if Globals.MET is None:
		Globals.MET = _ReadMET()
		
	#check if we needto filter or interpolate
	if Date is None and ut is None:
		#just return the lot here
		return Globals.MET
	elif not Date is None and ut is None:
		#here we either need a single date, or a range of dates to be returned
		if np.size(Date) == 1:
			use = np.where(Globals.MET.Date == Date)[0]
			return Globals.MET[use]
		else:
			use = np.where((Globals.MET.Date >= Date[0]) & (Globals.MET.Date <= Date[-1]))[0]
			return Globals.MET[use]
	else:
		#this bit assumes that the length of date and ut are equal, and
		#that we want the MET for a bunch of specific times
		use = np.where((Globals.MET.Date >= Date[0]) & (Globals.MET.Date <= Date[-1]))[0]
		udate = np.unique(Date)
		utc = np.array(ut)
		for i in range(0,udate.size):
			u = np.where(Date == udate[i])[0]
			if u.size > 0:
				utc[u] += TT.DateDifference(Globals.MET.Date[use[0]],Date[u])*24.0
		oldut = np.arange(use.size)*24.0
		f = interp1d(oldut,Globals.MET.MET[use],bounds_error=False,fill_value='extrapolate')
		METout = f(utc)
		out = np.recarray(METout.size,dtype=Globals.MET.dtype)
		out.Date = Date
		out.ut = ut
		out.MET = METout
		return out
