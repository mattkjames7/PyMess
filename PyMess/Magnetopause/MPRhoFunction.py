import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline

def MPRhoFunction(Rss=1.42,Alpha=0.5):
	Theta = (np.arange(179.0)[::-1])*np.pi/180.0
	R = Rss*(2.0/(1.0 + np.cos(Theta)))**Alpha
	x = R*np.cos(Theta)
	y = R*np.sin(Theta)
	f = InterpolatedUnivariateSpline(x,y)
	return f
