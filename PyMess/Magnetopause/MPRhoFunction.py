import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline

def MPRhoFunction(Rss=1.42,Alpha=0.5):
	'''
	Returns a spline function which provides a value for rho 
	(sqrt(y**2 + z**2)) as a function of x.
	
	Inputs:
		Rss: Subsolar point of the magnetopause in Rm.
		Alpha: Controls the flaring of the magnetopause, usually 0.5.
		
	Returns:
		InterpolatedUnivariateSpline object.
	'''
	Theta = (np.arange(179.0)[::-1])*np.pi/180.0
	R = Rss*(2.0/(1.0 + np.cos(Theta)))**Alpha
	x = R*np.cos(Theta)
	y = R*np.sin(Theta)
	f = InterpolatedUnivariateSpline(x,y)
	return f
