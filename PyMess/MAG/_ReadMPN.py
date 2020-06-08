import numpy as np
from RecarrayTools.ReadRecarray import ReadRecarray
import os
from ..Tools.ResampleTimeSeries import ResampleTimeSeries
from ._SaveMPN import _SaveMPN

def _ReadMPN(Date,Minute=False,res=None,DetectGaps=None,Autosave=True,Length=False):
	'''
	Read the data rotated into a coordinate system where Bx, By, Bz ==
	Bpol, Btor, Bpar
	
	'''
	path = MagGlobals.paths['MPN']
	if Minute:
		path += 'Minute/'
	else:
		path += 'Full/'
	fname = path + '{:08d}.bin'.format(Date)
	dtype = MagGlobals.dtypes['MPN']	
	
	if not os.path.isfile(fname):
		print('Data not found for this date...')
		if not Autosave:
			return np.recarray(0,dtype=dtype)

		else:
			print('Attempting to convert MSO data')
			status = _SaveMPN(Date,Minute)
			if not status:
				if Length:
					return 0
				else:
					return np.recarray(0,dtype=dtype)
	if Length:
		f = open(path + fname,'rb')
		n = np.fromfile(f,dtype='int32',count=1)[0]
		f.close()
		return n		
	data = ReadRecarray(fname,dtype)


	if res != None:
		UTo = np.array(data.ut)
		
		length = np.int32(86400/res)
		newdata = np.recarray(length,dtype=dtype)
		
		
		if DetectGaps != None:
			DG = DetectGaps
		else:
			DG = res

		tags = data.dtype.names
		newdata.ut = 24*np.arange(length,dtype='float32')/length
		newdata.Date = Date
		for t in tags:
			if not t in ['Date','ut']:
				newdata[t] = ResampleTimeSeries(data.ut,data[t],newdata.ut,DG/3600.0,UseSpline=True)

		if DetectGaps != None:
			#set Detect gaps to the largest number of seconds gap (5s is used elsewhere)
			MaxUTGapHr = DetectGaps/3600.0
			bad = np.zeros(length,dtype='bool')
			for i in range(0,UTo.size-1):
				if (UTo[i+1]-UTo[i]) > MaxUTGapHr:
					b = np.where((newdata.ut > UTo[i]) & ( newdata.ut <  UTo[i+1]))[0]
					bad[b] = True
			
			baddata = np.where(bad)[0]
			tags = ['BL','BM','BN']
			for t in tags:
				newdata[t][baddata] = np.float32(np.nan)
			
		return newdata
	else:
		return data
