import numpy as np
from .ReadMagData import ReadMagData
import KT17 as kt17
from ..Pos.GetAberrationAngle import GetAberrationAngle
from ._MSM2Dipolar import _MSM2Dipolar
from ..Pos.GetMercuryPos import GetMercuryPos

def MagRotatedData(Date,Minute=False,res=None,ModelParams=None,Ab=None,DetectGaps=None):
	'''
	This procedure should return magnetometer data rotated into 
	a coordinate system useful for studying waves, with components in
	the poloidal, toroidal and parallel directions.
	
	Inputs:
		Date: 32-bit integer containing the date with the format 
			yyyymmdd.
		Minute: Set to True to use minute resolution data, or False for
			full time resolution data.
		res: Tells the function to resample the MAG data to this time
			resolution in seconds.
		ModelParams: Parameters to use for the KT17 magnetic field model
			When set to None, the values used are calculated based on 
			Mercury's distance from the Sun.
		Ab: Aberration angle in degrees, set to None to calculate 
			automatically.
		DetectGaps: If not None, then the routine will search for gaps
			larger than DetectGaps in hours and insert NaNs, gaps 
			smaller than this are interpolated over.
			
	Returns:
		numpy.recarray
	'''
	if ModelParams is None:
		tmp = GetMercuryPos(Date)
		Rau = tmp.r
		ModelParams = [Rau,50.0]
	
	
	data = ReadMagData(Date,Minute,res,Ab,DetectGaps=DetectGaps)
	
	t=data.ut
	#data already rotated into aberrated corrdinates
	b1,b2,b3 = data.Bx,data.By,data.Bz
	p1,p2,p3 = data.Xmsm,data.Ymsm,data.Zmsm
	
	#now to get model field vectors in aberrated coordinates 
	#(no need to aberrate them again) including MP check
	m1,m2,m3 = kt17.ModelField(p1,p2,p3,ModelParams)

	#rotate data vectors, then model vectors, then subtract parallel component
	tx,ty,tz = _MSM2Dipolar(b1,b2,b3,m1,m2,m3,p1,p2,p3)
	ttx,tty,ttz = _MSM2Dipolar(m1,m2,m3,m1,m2,m3,p1,p2,p3)
	tz-=ttz

	b1 = tx
	b2 = ty
	b3 = tz

	#returned coordinates will be in aberrated coords
	# Bx,By,Bz == Bpol, Btor, Bpar
	dtype=[('Date','int32'),('ut','float32'),('Bx','float32'),('By','float32'),('Bz','float32'),('Xmsm','float32'),('Ymsm','float32'),('Zmsm','float32')]
	data = np.recarray(t.size,dtype=dtype)
	data.ut = t
	data.Bpol = b1
	data.Btor = b2
	data.Bpar = b3
	data.Xmsm = p1
	data.Ymsm = p2
	data.Zmsm = p3
	
	return data
