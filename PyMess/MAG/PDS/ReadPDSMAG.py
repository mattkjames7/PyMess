import numpy as np
import PyFileIO as pf
import DateTimeTools as TT
from .. import MagGlobals
from ...Tools.ContUT import ContUT
from ...Pos.GetRegion import GetRegion

def ReadPDSMAG(fname):
	'''
	This will read in the .TAB datafile and output a numpy.recarray
	
	Inputs:
		fname: file name and path
	'''
	pdsdtype = [	('Year','int32'),
					('DOY','int32'),
					('Hour','int32'),
					('Min','int32'),
					('Sec','float32'),
					('MET','float32'),
					('Xmso','float32'),
					('Ymso','float32'),
					('Zmso','float32'),
					('Bx','float32'),
					('By','float32'),
					('Bz','float32'),
					('Loc','U2')]
					
	data = pf.ReadASCIIData(fname,False,dtype=pdsdtype)
	
	dtype = MagGlobals.dtypes['MSM']
				
	n = data.size
	out = np.recarray(n,dtype)
	
	out.Date = np.array([TT.DayNotoDate(data.Year[i],data.DOY[i])[0] for i in range(0,n)])
	out.ut = np.float32(data.Hour) + np.float32(data.Min)/60.0 + np.float32(data.Sec)/3600.0
	out.utc = ContUT(out.Date,out.ut)
	out.Xmso = data.Xmso/2440.0
	out.Ymso = data.Ymso/2440.0
	out.Zmso = data.Zmso/2440.0
	out.Xmsm = data.Xmso/2440.0
	out.Ymsm = data.Ymso/2440.0
	out.Zmsm = data.Zmso/2440.0 - 0.196
	out.Bx = data.Bx
	out.By = data.By
	out.Bz = data.Bz
	out.Loc = GetRegion(out.Date,out.ut,out.utc,Verbose=False)

	return out
