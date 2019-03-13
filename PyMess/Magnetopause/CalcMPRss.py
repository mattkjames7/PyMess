import numpy as np

def CalcMPRss(xmsm,ymsm,zmsm,Alpha=0.5):
	'''
	Calculates the distance of the subsolar magnetopause given the 
	position of a MP crossing observation, assuming the	Shue et al. 
	shape.
	
	Inputs:
		xmsm,ymsm,zmsm: Cartesian MSM coordinates of the MP observations.
		Alpha: Flaring parameter of the magnetopause.
		
	Returns:
		Rss for each observation
	'''
	rho = np.sqrt(ymsm**2 + zmsm**2)
	r = np.sqrt(xmsm**2 + rho**2)
	costheta = xmsm/r
	Rss = r/((2.0/(1.0+costheta))**Alpha)
	
	return Rss
