import numpy as np
from scipy.optimize import minimize

def _D2(E,Rss,Alpha,xp,yp):
	'''
	Function to calculate the distance between the guessed point on the 
	magnetopause and the reference position.
	
	Inputs:
		E: The guessed angle - also the target.
		Rss: Subsolar distance of the magnetopause.
		Alpha: Flaring parameter.
		xp: Reference position in x MSM direction.
		yp: Reference position in rho (sqrt(y**2 + z**2)) MSM direction.
		
	Returns:
		floating point to be minimized
	
	'''
	cosE = np.cos(E)
	sinE = np.sin(E)
	
	r = Rss*(2.0/(1.0 + cosE))**Alpha
	
	return xp**2 + yp**2 + r**2 - 2.0*r*(xp*cosE + yp*sinE)


def MinimizeMPDist(xin,yin,Rss=1.42,Alpha=0.5):
	'''
	Finds closest point on the magnetopause in a 2D plane given x and y
	starting coordinates.
	
	Inputs:
		xin: Position(s) in x MSM direction.
		yin: Position(s) in rho (sqrt(y**2 + z**2)) MSM direction.
		Rss: Subsolar distance of the magnetopause.
		Alpha: Flaring parameter.
		
	Returns:
			tuple containing:
			(success-boolean,optimized angle along magnetopause-float,
			radial distance of magnetopause-float)
	'''
	if np.size(xin) == 1:
		x = np.array([xin])
		y = np.array([yin])
	else:
		x = np.array(xin)
		y = np.array(yin)		
	
	n = np.size(x)
	s = np.zeros(n,dtype='bool')
	E = np.zeros(n,dtype='float32')
	r = np.zeros(n,dtype='float32')
	for i in range(0,n):
		res = minimize(_D2,0.0,args=(Rss,Alpha,x[i],y[i]))
	
		if res.success:
			E[i] = res.x
			r[i] = Rss*(2.0/(1.0 + np.cos(E[i])))**Alpha
			s[i] = True
		else:
			E[i] = np.nan
			r[i] = np.nan
			s[i] = False
			
	return s,E,r
		
def NearestMP3d(x,y,z,Rss=1.42,Alpha=0.5):
	'''
	Finds the closest point on the Hermean magnetopause to a given set
	of positions in MSM coordinates.
	
	Inputs:
		x,y,z: Input cartesian MSM coordinates.
		Rss: Subsolar distance of the magnetopause.
		Alpha: Flaring parameter.
		
	Returns:
		Tuple containing the nearest positions along the magnetopause.
	
	'''
	rho = np.sqrt(y**2 + z**2)
	
	s,E,r = MinimizeMPDist(x,rho,Rss,Alpha)
	
	xMP = r*np.cos(E)
	rhoMP = r*np.sin(E)
	
	phi = np.arctan2(z,y)
	
	yMP = rhoMP*np.cos(phi)
	zMP = rhoMP*np.sin(phi)
	
	return (xMP,yMP,zMP)
