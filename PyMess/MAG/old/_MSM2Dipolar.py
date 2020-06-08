import numpy as np

def _MSM2Dipolar(bx,by,bz,mbx,mby,mbz,x,y,z):
	'''
	Rotates magnetic field data based upon model field.
	
	Inputs:
		bx,by,bz: original magnetic field vectors in MSO/MSM.
		mbx,mby,mbz: Model field in MSO/MSM.
		x,y,z: spacecraft position in MSM coordinates.
		
	Returns:
		(x,y,z) rotated magnetic field vectors
		
	'''
	x0=np.array(bx)
	y0=np.array(by)
	z0=np.array(bz)

	mx0=np.array(mbx)
	my0=np.array(mby)
	mz0=np.array(mbz)	

	px=np.array(x)
	py=np.array(y)
	pz=np.array(z)
	
	#find MLT and transform x and y such that x1 points 
	#away from Mercury in the equatorial plane
	a=np.arctan2(py,(-px))
	
	x1=x0*np.cos(a) - y0*np.sin(a)
	y1=x0*np.sin(a) + y0*np.cos(a)
	z1=z0

	mx1=mx0*np.cos(a) - my0*np.sin(a)
	my1=mx0*np.sin(a) + my0*np.cos(a)
	mz1=mz0
	
	
	#find tilt angle of the field line (-b) and rotate z1 
	#and x1 around y1 such that x2 = 0 and z2 = sqrt(x1^2 + z1^2)
	b=-np.arctan2(mx1,mz1)
	
	x2=z1*np.sin(b) + x1*np.cos(b)
	y2=y1
	z2=z1*np.cos(b) - x1*np.sin(b)

	mx2=mz1*np.sin(b) + mx1*np.cos(b)
	my2=my1
	mz2=mz1*np.cos(b) - mx1*np.sin(b)	
	
	
	#finally, rotate z2 and y2 around x2 such that z3 is pointed
	#along the field line (hopefully)
	c=np.arctan2(my2,mz2)
	
	x3=x2
	y3=y2*np.cos(c) - z2*np.sin(c)
	z3=y2*np.sin(c) + z2*np.cos(c)
	
	return (x3,y3,z3)
