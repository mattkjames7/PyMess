import numpy as np
import PyFileIO as pf
import DateTimeTools as TT

def ReadPDSMAG(fname):
	'''
	This will read in the .TAB datafile and output a numpy.recarray
	
	Inputs:
		fname: file name and path
	'''
	pdsdtype = dtype=[('Year','int32'),('DOY','int32'),('Hour','int32'),
						('Min','int32'),('Sec','float32'),('MET','float32'),
						('Xmso','float32'),('Ymso','float32'),('Zmso','float32'),
						('Bx','float32'),('By','float32'),('Bz','float32')]
	data = pf.ReadASCIIData(fname,False,dtype=pdsdtype)
	
	dtype = [('Date','int32'),('ut','float32'),
			('Xmso','float32'),('Ymso','float32'),('Zmso','float32'),
			('Xmsm','float32'),('Ymsm','float32'),('Zmsm','float32'),
				('Bx','float32'),('By','float32'),('Bz','float32')]	
				
	n = data.size
	out = np.recarray(n,dtype)
	
	out.Date = np.array([TT.DayNotoDate(data.Year[i],data.DOY[i]) for i in range(0,n)])
	out.ut = np.float32(data.Hour) + np.float32(data.Min)/60.0 + np.float32(data.Sec)/3600.0
	out.Xmso = data.Xmso/2440.0
	out.Ymso = data.Ymso/2440.0
	out.Zmso = data.Zmso/2440.0
	out.Xmsm = data.Xmso/2440.0
	out.Ymsm = data.Ymso/2440.0
	out.Zmsm = data.Zmso/2440.0 - 0.196
	out.Bx = data.Bx
	out.By = data.By
	out.Bz = data.Bz

	return out
