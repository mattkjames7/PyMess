import numpy as np

def RotTrans(x,y,a):
	'''
	Performs rotational transform on x and y (anticlockwise).
	
	Inputs:
		x: original x coordinate(s)
		y: original y coordinate(s)
		a: angle(s) by which to rotate x and y
	
	Returns:
		Transformed x' and y'.
	'''
	ox = x*np.cos(a) - y*np.sin(a)
	oy = x*np.sin(a) + y*np.cos(a)
	
	return (ox,oy)
