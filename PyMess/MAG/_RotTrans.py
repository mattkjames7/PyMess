import numpy as np

def _RotTrans(x,y,a):

	ox = x*np.cos(a) - y*np.sin(a)
	oy = x*np.sin(a) + y*np.cos(a)
	
	return (ox,oy)
