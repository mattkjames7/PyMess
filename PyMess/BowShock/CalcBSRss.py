import numpy as np

def CalcBSRss(xmsm,ymsm,zmsm,e=0.993):
	'''
	Calculates the distance of the subsolar bow shock given the 
	position of a BS crossing observation.
	
	Inputs:
		xmsm,ymsm,zmsm: Cartesian MSM coordinates of the BS observations.
		e: eccentricity of the bow shockk function.
		
	Returns:
		Rss for each observation
	'''
	x0 = 0.5
	r = np.sqrt((xmsm-x0)**2 + ymsm**2 + zmsm**2)
	p = r/e + xmsm - x0
	Rss = p*e/(1+e) + x0
	
	return (p,Rss)
