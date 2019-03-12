import numpy as np

def MPNormal(x,y,z):
	'''
	Calculates the normal unit vector of the magnetopause at some given
	location.
	
	Inputs:
		x,y,z: MSM coordinates of psotion on magnetopause.
	
	Returns:
		unit vector in the forma of a tuple of x, y and z components.
	
	'''
	r = np.sqrt(x**2 + y**2 + z**2)
	nx = 2.0*x + (x**2)/r + r
	ny = 2.0*y + x*y/r
	nz = 2.0*z + x*z/r
	N = np.sqrt(nx**2 + ny**2 + nz**2)
	return (nx/N,ny/N,nz/N)
