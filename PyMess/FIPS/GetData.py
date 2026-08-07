import numpy as np
from .ReadData import ReadData
from .. import Globals
import DateTimeTools as TT


def _AppendTimeFields(data,FileDate):
	"""Add Date, UT and continuous-UT fields to MET-only FIPS data."""
	fields = data.dtype.names or ()
	missing = [name for name in ('Date','ut','utc') if name not in fields]
	if not missing:
		return data

	if ('Date' not in fields or 'ut' not in fields) and 'MET' not in fields:
		raise ValueError('FIPS data contain neither calendar time nor MET')

	if 'Date' in fields and 'ut' in fields:
		date = np.asarray(data.Date,dtype='int32')
		ut = np.asarray(data.ut,dtype='float32')
	else:
		epoch = (
			Globals.FIPSMETResetUnix
			if int(np.asarray(FileDate).reshape(-1)[0]) >= Globals.FIPSMETResetDate
			else Globals.FIPSMET0Unix
		)
		date,ut = TT.UnixTimetoDate(
			np.asarray(data.MET,dtype='float64') + epoch
		)
		date = np.asarray(date,dtype='int32')
		ut = np.asarray(ut,dtype='float32')
	utc = np.asarray(TT.ContUT(date,ut),dtype='float64')

	add_dtype = {'Date':'int32','ut':'float32','utc':'float64'}
	dtype = list(data.dtype.descr) + [(name,add_dtype[name]) for name in missing]
	out = np.recarray(data.size,dtype=dtype)
	for name in fields:
		out[name] = data[name]
	if 'Date' in missing:
		out.Date = date
	if 'ut' in missing:
		out.ut = ut
	if 'utc' in missing:
		out.utc = utc
	return out

def GetData(Date,ut=[0.0,24.0],Type='60H',Verbose=True):
	'''
	Retrieves FIPS data from a specific time range
	
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
		n += ReadData(dates[i],Type,Length=True,quiet=not Verbose)
	if Verbose:
			print('\rCounting records in file {0} of {1} ({2})'.format(i+1,nd,n))
	#now load the data
	p = 0
	for i in range(0,nd):
		if Verbose:
			print('\rReading file {0} of {1}'.format(i+1,nd),end='')
		tmp = ReadData(dates[i],Type,quiet=not Verbose)
		tmp = _AppendTimeFields(tmp,dates[i])
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
