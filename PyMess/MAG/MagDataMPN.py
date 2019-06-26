import numpy as np
from .ReadMagData import ReadMagData

from ..Tools.RotTrans import RotTrans
from scipy.interpolate import InterpolatedUnivariateSpline

def MagDataMPN(Date,Minute=False,res=None,Rsm=1.42,Ab=None):
	from ..Magnetopause.MSMtoMPN import MSMtoMPN
	from ..Magnetopause.NearestMPPoint import NearestMP3d
	from ..Magnetopause.MPNormal import MPNormal

	'''
	This procedure should return magnetometer data rotated into 
	a magnetopause normal coordinate system based on the Shue et al
	model.
	
	Inputs:
		Date: 32-bit integer containing the date with the format 
			yyyymmdd.
		Minute: Set to True to use minute resolution data, or False for
			full time resolution data.
		res: Tells the function to resample the MAG data to this time
			resolution in seconds.
		Rsm: Subsolar radius of the magnetopause (usually 1.42 on average)
		Ab: Aberration angle in degrees, set to None to calculate 
			automatically.

			
	Returns:
		numpy.recarray
	'''	
	#read minute data first
	MinData = ReadMagData(Date,True,Ab=Ab)
	
	#if minute == True then use imported function
	if Minute == True:
		BN,BM,BL,pN,pM,pL,xMP,yMP,zMP,nx,ny,nz = MSMtoMPN(MinData.Bx,MinData.By,MinData.Bz,MinData.Xmsm,MinData.Ymsm,MinData.Zmsm,True)
		ut = MinData.ut
		Bx = MinData.Bx
		By = MinData.By
		Bz = MinData.Bz
		Xmsm = MinData.Xmsm
		Ymsm = MinData.Ymsm
		Zmsm = MinData.Zmsm
	#otherwise, use the minute position to get an array of normals and magnetopause positions, then interpolat for the full data
	else:
		txMP,tyMP,tzMP = NearestMP3d(MinData.Xmsm,MinData.Ymsm,MinData.Zmsm)
		tnx,tny,tnz = MPNormal(txMP,tyMP,tzMP)
		
		FullData = ReadMagData(Date,False,res,Ab=Ab)
		
		gd = np.where(np.isfinite(tnx) & np.isfinite(tny) & np.isfinite(tnz))[0]
		gdMP = np.where(np.isfinite(txMP) & np.isfinite(tyMP) & np.isfinite(tzMP))[0] 
		
		if gd.size > 3  and gdMP.size > 4:
			f = InterpolatedUnivariateSpline(MinData.ut[gdMP],txMP[gdMP])
			xMP = f(FullData.ut)
			f = InterpolatedUnivariateSpline(MinData.ut[gdMP],tyMP[gdMP])
			yMP = f(FullData.ut)
			f = InterpolatedUnivariateSpline(MinData.ut[gdMP],tzMP[gdMP])
			zMP = f(FullData.ut)

			f = InterpolatedUnivariateSpline(MinData.ut[gd],tnx[gd])
			nx = f(FullData.ut)
			f = InterpolatedUnivariateSpline(MinData.ut[gd],tny[gd])
			ny = f(FullData.ut)
			f = InterpolatedUnivariateSpline(MinData.ut[gd],tnz[gd])
			nz = f(FullData.ut)
			
			
			#now rotate full data
			theta1 = np.arctan2(ny,nx)
		
			px_,pM = RotTrans(FullData.Xmsm,FullData.Ymsm,-theta1)
			Bx_,BM = RotTrans(FullData.Bx,FullData.By,-theta1)	
			
			theta2 = np.arctan2(nz,np.sqrt(nx**2 + ny**2))
			
			pN,pL = RotTrans(px_,FullData.Zmsm,-theta2)
			BN,BL = RotTrans(Bx_,FullData.Bz,-theta2)


			ut = FullData.ut
			Bx = FullData.Bx
			By = FullData.By
			Bz = FullData.Bz
			Xmsm = FullData.Xmsm
			Ymsm = FullData.Ymsm
			Zmsm = FullData.Zmsm		
		else:
			ut = np.array([])
			
	n = np.size(ut)
	dtype = [('ut','float32'),('BN','float32'),('BM','float32'),('BL','float32'),('Bx','float32'),('By','float32'),('Bz','float32'),('pN','float32'),('pM','float32'),('pL','float32'),
			('xMP','float32'),('yMP','float32'),('zMP','float32'),('nx','float32'),('ny','float32'),('nz','float32'),('E','float32'),
			('r','float32'),('phi','float32'),('Xmsm','float32'),('Ymsm','float32'),('Zmsm','float32')]
	
	data = np.recarray(n,dtype=dtype)
	if n == 0:
		return data
	
	data.ut = ut
	data.BN = BN
	data.BM = BM
	data.BL = BL
	data.Bx = Bx
	data.By = By
	data.Bz = Bz
	data.Xmsm = Xmsm
	data.Ymsm = Ymsm
	data.Zmsm = Zmsm
	data.pN = pN
	data.pM = pM
	data.pL = pL
	data.xMP = xMP
	data.yMP = yMP
	data.zMP = zMP
	data.nx = nx
	data.ny = ny
	data.nz = nz
	data.r = np.sqrt(xMP**2 + yMP**2 + zMP**2)
	data.phi = np.arctan2(zMP,np.abs(yMP))
	data.E = np.arccos(xMP/data.r)*180.0/np.pi*np.sign(yMP)
	
	
	return data
