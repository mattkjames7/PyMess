import numpy as np
from .MPNormal import MPNormal
from .NearestMPPoint import NearestMP3d
from Misc.RotTrans import RotTrans

def MSMtoMPN(vx,vy,vz,px,py,pz,ReturnAll=False):
	
	#get nearest MP point
	xMP,yMP,zMP = NearestMP3d(px,py,pz)
	
	#obtain normal vector
	nx,ny,nz = MPNormal(xMP,yMP,zMP)
	
	#find first angle and rotate about z
	theta1 = np.arctan2(ny,nx)

	px_,pM = RotTrans(px,py,-theta1)
	vx_,vM = RotTrans(vx,vy,-theta1)
	
	#find second angle and rotate about M
	
	theta2 = np.arctan2(nz,np.sqrt(nx**2 + ny**2))
	
	pN,pL = RotTrans(px_,pz,-theta2)
	vN,vL = RotTrans(vx_,vz,-theta2)
	
	if ReturnAll:
		return (vN,vM,vL,pN,pM,pL,xMP,yMP,zMP,nx,ny,nz)
	else:
		return (vN,vM,vL,pN,pM,pL)
