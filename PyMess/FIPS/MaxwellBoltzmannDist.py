import numpy as np

k_B = 1.38064852e-23
e = 1.6022e-19


def MaxwellBoltzmannDist(v,n,T,m):
	'''
	This function outputs the phase space density (PSD) of a Maxwell-
	Boltzmann function given a temperature, density and velocity array.
	
	Inputs:
		v: Particle velocity array (m/s).
		n: Density (m^-3).
		T: Temperature (K).
		m: Particle mass (Kg).
		
	Returns:
		Array of PSD corresponding to each velocity in v.
	'''
	vth = np.sqrt(k_B*T/m)
	f = n* (1.0/(vth*(np.sqrt(2.0*np.pi)))**3.0) * np.exp(-v**2.0/(2.0*vth**2.0))
	return f


def MaxwellBoltzmannDistCts(v,n,T,m,Eff=1.0,dOmega=1.15*np.pi,nSpec=1.0,Tau=0.095,g=8.31e-5):
	'''
	This function outputs the expected count rate fot a Maxwell-
	Boltzmann function given a temperature, density and velocity array.
	
	Inputs:
		v: Particle velocity array (m/s).
		n: Density (m^-3).
		T: Temperature (K).
		m: Particle mass (Kg).
		Eff: Efficiency for detecting the particle species in question.
		dOmega: The effective instrument field of view (sr).
		nSpec: The number of spectra used.
		Tau: Accumulation time for a single spectrum (s).
		g: Energy-geometric factor of the instrument mm^2 Ev/Ev
		
	Returns:
		Array of counts corresponding to each velocity in v.
	'''
	vth = np.sqrt(k_B*T/m)
	
	v4 = v**4
	A = (Tau*g*dOmega*n*ProtonEff*nSpec)/(20*(vth*np.sqrt(2.0*np.pi))**3)
	C = A*v4*np.exp(-(v**2)/(2.0*vth**2))
	return C/1000.0
