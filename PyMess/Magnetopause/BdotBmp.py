import numpy as np
import KT17 as kt17
from ..MAG.ReadMagData import ReadMagData
from scipy.interpolate import InterpolatedUnivariateSpline
from .NearestMPPoint import NearestMP3d


def BdotBmp(Date,ut=[0.0,24.0],Minute=False,res=None,Ab=None,indata=None):
	'''
	Returns the dot product of the meaesured magnetic field with the 
	KT17 magnetic field just within the magnetopause.
	
	
	Inputs:
		Date: 32-bit integer with the format yyyymmdd.
		ut: 2 element list, tuple or array containing the start and end
			times.
		Minute: Boolean, loads miute dat if True, full data if False.
		res: Resample interval in seconds, if set to None, then data
			is not resampled.
		Ab: Aberration angle in degrees, set to None to calculate 
			automatically.
		indata: Pass a numpy.ndarray containing the magnetometer data to
			this keyword if the data is already loaded.
			
	Returns:
		tuple containing time,dot product and the angle between the two 
		fields
	'''
	#load mag data
	if indata is None:
		data = ReadMagData(Date,Minute,res,Ab=Ab)
	else:
		data = indata.copy()
	use = np.where((data.ut >= ut[0]) & (data.ut <= ut[1]))[0]
	data = data[use]
	
	Bmag = np.sqrt(data.Bx**2 + data.By**2 + data.Bz**2)
	
	#find magnetopause footprint
	if Minute or (ut[1]-ut[0])*60.0 < 5.0:
		xmp,ymp,zmp = NearestMP3d(data.Xmsm,data.Ymsm,data.Zmsm)
	else:
		mindata = ReadMagData(Date,True,Ab=Ab)
		use = np.where((mindata.ut >= ut[0]) & (mindata.ut <= ut[1]))[0]
		mindata = mindata[use]		
		mxmp,mymp,mzmp = NearestMP3d(mindata.Xmsm,mindata.Ymsm,mindata.Zmsm)
		f = InterpolatedUnivariateSpline(mindata.ut,mxmp)
		xmp = f(data.ut)
		f = InterpolatedUnivariateSpline(mindata.ut,mymp)
		ymp = f(data.ut)
		f = InterpolatedUnivariateSpline(mindata.ut,mzmp)
		zmp = f(data.ut)

	#find MP field
	#bxmp,bymp,bzmp = kt14.ModelField(data.Xmsm,data.Ymsm,data.Zmsm,False)
	bxmp,bymp,bzmp = kt14.ModelField(xmp,ymp,zmp,False)
	BmagMP = np.sqrt(bxmp**2 + bymp**2 + bzmp**2)

	#dot product
	BdtBmp = data.Bx*bxmp + data.By*bymp + data.Bz*bzmp

	#get angle
	angle = np.arccos(BdtBmp/(Bmag*BmagMP))*180.0/np.pi
	
	dtype = [('Date','int32'),('ut','float32'),('BdotBmp','float32'),('Angle','float32')]
	out = np.recarray(data.size,dtype=dtype)
	out.Date = data.ut
	out.ut = data.ut
	out.BdotBmp = BdotBmp
	out.Angle = angle
	
	return out
	
