import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline

def MPxFunction(Rss=1.42,Alpha=0.5):
	'''
	Returns spline function which provides a value of x given rho
	(sqrt(y**2 + z**2)). 
	
	Inputs:
		Rss: Subsolar point of the magnetopause in Rm.
		Alpha: Controls the flaring of the magnetopause, usually 0.5.
		
	Returns:
		InterpolatedUnivariateSpline object, or similar.
	'''
	Theta = (np.arange(359.0)-179.0)*np.pi/180.0
	R = Rss*(2.0/(1.0 + np.cos(Theta)))**Alpha
	x = R*np.cos(Theta)
	y = R*np.sin(Theta)
	
	if Alpha > 0.5:
		f = InterpolatedUnivariateSpline(y,x)
		return f
	else:
		def F(rho):
			if np.size(rho) == 1:
				r = np.array([rho])
			else:
				r = np.array(rho)
			out = np.zeros(r.size,dtype='float32')
			for i in range(0,r.size):
				if np.abs(r[i]) > np.max(y):
					out[i] = np.inf
				else:
					f = InterpolatedUnivariateSpline(y,x)
					out[i] = f(r[i])
			return out
		return F


def MPxDist(x,rho,Rss=1.42,Alpha=0.5):
	'''
	Calculates the distance along the x axis to the magnetopause.
	
	Inputs:
		x: coordinates in the x direction.
		rho: coordinates in the sqrt(y**2 + z**2) direction.
		Rss: Subsolar point of the magnetopause in Rm.
		Alpha: Controls the flaring of the magnetopause, usually 0.5.
	
	Returns:
		Distance along the x axis between (x,rho) and the magnetopause.
	'''
	F = MPxFunction(Rss,Alpha)
	return np.abs(x-F(rho))
