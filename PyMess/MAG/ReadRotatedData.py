import numpy as np
from RecArrayTools.ReadRecarray import ReadRecarray
import os
import interp

def ReadRotatedData(Date,Minute=False,res=None,DetectGaps=None):
	
	if Minute:
		path = os.getenv('MESSENGER_PATH')+'/MAG/Rotated/Minute/'
	else:
		path = os.getenv('MESSENGER_PATH')+'/MAG/Rotated/Full/'
	fname = path + '{:08d}-bin'.format(Date)
	dtype=[('ut','float32'),('Bpol','float32'),('Bphi','float32'),('Bpar','float32'),('Xmsm','float32'),('Ymsm','float32'),('Zmsm','float32')]
	data = ReadRecarray(fname,dtype)


	if res != None:
		UTo = np.array(data.ut)
		
		length=np.int32(86400/res)
		newdata = np.recarray(length,dtype=dtype)
		
		
		if DetectGaps != None:
			DG = DetectGaps
		else:
			DG = res
		ntags = np.size(data.dtype.names)
		newdata.ut=24*np.arange(length,dtype='float32')/length
		newdata.Date = Date
		good = np.where(np.isfinite(data.Bphi))[0]
		for i in range(1,ntags):
			
			newdata[newdata.dtype.names[i]] = interp.ResampleTimeSeries(data.ut,data[data.dtype.names[i]],newdata.ut,DG/3600.0,UseSpline=True)

		if DetectGaps != None:
			#set Detect gaps to the largest number of seconds gap (5s is used elsewhere)
			MaxUTGapHr = DetectGaps/3600.0
			bad = np.zeros(length,dtype='bool')
			for i in range(0,UTo.size-1):
				if (UTo[i+1]-UTo[i]) > MaxUTGapHr:
					b=np.where((newdata.ut > UTo[i]) & ( newdata.ut <  UTo[i+1]))[0]
					bad[b] = True
			
			baddata = np.where(bad)[0]
			dtags = ['Bpol','Bphi','Bpar']
			for i in range(0,3):
				if dtags[i] in data.dtype.names:
					newdata[dtags[i]][baddata] = np.float32(np.nan)
			
		return newdata
	else:
		return data
