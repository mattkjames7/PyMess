import numpy as np

def WithinMP(x,rho,Rss=1.42,Alpha=0.5):
	
	theta = np.arctan2(rho,x)
	r = np.sqrt(x**2 + rho**2)
	Rtheta = Rss*(2.0/(1.0+np.cos(theta)))**Alpha
	return Rtheta > r
