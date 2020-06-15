import numpy as np
from ..Tools.ContUT import ContUT

import DateTimeTools as TT

def GetRegion(Date,ut,utc=None,Verbose=False):
	'''
	For an array of dates and times, return an array showing what region 
	Messenger was within around the magnetosphere at each time.
	
	Inputs
	======
	Date : int
		Array of integer dates, formay yyyymmdd
	ut : float
		Array of times, where the time is in hours since the beginning 
		of the day
		
		
	Returns
	=======
	Loc : str
		Array of strings, where:
			'UK' : Unknown region
			'SW' : Solar wind
			'BS' : Within bowshock crossing (mixture of SW and MSH)
			'SH' : Within the magnetosheath
			'MP' : In magnetopause crossing region
			'MS' : Within magnetosphere
	'''

	from ..Magnetopause.GetMPCrossings import GetMPCrossings
	from ..Magnetopause.GetMSTimes import GetMSTimes
	from ..Magnetosheath.GetMSHCrossings import GetMSHCrossings
	from ..BowShock.GetBSCrossings import GetBSCrossings
	from ..BowShock.GetSolarWindTimes import GetSolarWindTimes
	#turn input into array
	Date = np.array([Date]).flatten()
	ut = np.array([ut]).flatten()
	
	#continuous time
	if utc is None:
		utc = ContUT(Date,ut)
	else:
		utc = np.array([utc]).flatten()
	#get all of the sets of crossings
	sw = GetSolarWindTimes()
	bs = GetBSCrossings()
	sh = GetMSHCrossings()
	mp = GetMPCrossings()
	ms = GetMSTimes()
	
	#create a list
	cr = [sw,bs,sh,mp,ms]
	lc = ['SW','BS','SH','MP','MS']

	#output
	Loc = np.zeros(ut.size,dtype='U2') 
	Loc[:] = 'UK'
	
	#find the date limits and pad with one day
	Date0 = TT.MinusDay(Date.min())
	Date1 = TT.PlusDay(Date.max())
	
	#loop through each region
	for i in range(0,5):
		C = cr[i]
		L = lc[i]
		
		if Verbose:
			print('Scanning for times within {:s}'.format(L))
		
		#limit to within date limits
		use = np.where((C.Date0 >= Date0) & (C.Date1 <= Date1))[0]
		c = C[use]
		cutc0 = ContUT(c.Date0,c.ut0)
		cutc1 = ContUT(c.Date1,c.ut1)
		
		#loop through each element and assign labels
		for j in range(c.size):
			if Verbose:
				print('\r{:d} of {:d} ({:6.2f}%)'.format(j+1,c.size,100.0*(j/c.size)),end='')
			use = np.where((utc >= cutc0[j]) & (utc <= cutc1[j]))[0]
			Loc[use] = L
		if Verbose:
			print('\r{:d} of {:d} ({:6.2f}%)'.format(j+1,c.size,100.0))
		
	return Loc
