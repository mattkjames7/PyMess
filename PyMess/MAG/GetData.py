import numpy as np
import DateTimeTools as TT
from ._ReadMSM import _ReadMSM
from ._ReadDip import _ReadDip
from ._ReadMPN import _ReadMPN
from . import MagGlobals 

def GetData(Date,ut=[0.0,24.0],Type='MSO',Minute=False,res=None,
			DetectGaps=None,Autosave=True,Ab=None,Verbose=True):
	'''
	Retrieves MAG data from a specific time range
	
	'''
	
	#get a list of dates
	if np.size(Date) == 1:
		#just a single date
		date0 = Date
		date1 = Date
		dates = np.array([Date])
	elif np.size(Date) > 2: 
		#list of specific dates
		date0 = np.min(Date)
		date1 = np.max(Date)
		dates = np.array(Date)
	else:
		#2 dates (start and end)
		date0 = np.min(Date)
		date1 = np.max(Date)
		tmp = np.array(date0)
		dates = [tmp]
		while tmp < date1:
			tmp = TT.PlusDay(tmp)
			dates.append(tmp)
		dates = np.array(dates)
		

	#work out the size of the output array
	nd = np.size(dates)
	n = 0
	for i in range(0,nd):
		if Verbose:
			print('\rCounting records in file {0} of {1} ({2})'.format(i+1,nd,n),end='')
		if Type in ['MSO','MSM']:
			n += _ReadMSM(dates[i],Minute=Minute,res=res,Ab=Ab,DetectGaps=DetectGaps,Length=True)
		elif Type == 'MPN':
			n += _ReadMPN(dates[i],Minute=Minute,res=res,DetectGaps=DetectGaps,Autosave=Autosave,Length=True)
		elif Type == 'Dip':
			n += _ReadDip(dates[i],Minute=Minute,res=res,DetectGaps=DetectGaps,Autosave=Autosave,Length=True)
		
	if Verbose:
			print('\rCounting records in file {0} of {1} ({2})'.format(i+1,nd,n))
	
	if n == 0:
		return np.recarray(0,dtype=MagGlobals.dtypes[Type])
	
	#now load the data
	p = 0
	for i in range(0,nd):
		if Verbose:
			print('\rReading file {0} of {1}'.format(i+1,nd),end='')
		if Type in ['MSO','MSM']:
			tmp = _ReadMSM(dates[i],Minute=Minute,res=res,Ab=Ab,DetectGaps=DetectGaps,Length=False)
		elif Type == 'MPN':
			tmp = _ReadMPN(dates[i],Minute=Minute,res=res,DetectGaps=DetectGaps,Autosave=Autosave,Length=False)
		elif Type == 'Dip':
			tmp = _ReadDip(dates[i],Minute=Minute,res=res,DetectGaps=DetectGaps,Autosave=Autosave,Length=False)
		if p == 0:
			out = np.recarray(n,dtype=tmp.dtype)
		out[p:p+tmp.size] = tmp
		p += tmp.size
	if Verbose:
		print()

	#limit to within the times specified in ut
	if date0 == date1:
		use = np.where((out.ut >= ut[0]) & (out.ut <= ut[1]))[0]
	else:
		use = np.where( ((out.Date == date0) & (out.ut >= ut[0])) |
						((out.Date > date0) & (out.Date < date1)) |
						((out.Date == date1) & (out.ut <= ut[1])))[0]
	
	return out[use]
