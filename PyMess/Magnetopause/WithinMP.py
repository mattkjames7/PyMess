import numpy as np

def WithinMP(x,rho,Rss=1.42,Alpha=0.5):
	'''
	Determines if a set of x and rho (sqrt(y**2 + z**2)) coordinates are
	within the magnetopause boundary or not.
	
	Inputs:
		x: Position(s) in x MSM direction.
		rho: Position(s) in rho MSM direction.
		Rss: Distance of the subsolar point on the magnetopause.
		Alpha: Magnetopause flaring parameter.
		
	Returns:
		boolean(s) where True means that the position is within the 
		magnetopause
	'''
	theta = np.arctan2(rho,x)
	r = np.sqrt(x**2 + rho**2)
	Rtheta = Rss*(2.0/(1.0+np.cos(theta)))**Alpha
	return Rtheta > r
