import numpy as np
from ..Tools.Gamma.Gamma import Gamma

k_B = 1.38064852e-23

def KappaDist(v,n,T,K,m):
	'''
	This function outputs the phase space density (PSD) of a Kappa 
	distribution function given a temperature, density and velocity array.
	
	Inputs:
		v: Particle velocity array (m/s).
		n: Density (m^-3).
		T: Temperature (K).
		K: Kappa parameter.
		m: Particle mass (Kg).
		
	Returns:
		Array of PSD corresponding to each velocity in v.
	'''
	v = np.float64(v)
	n = np.float64(n)
	T = np.float64(T)
	K = np.float64(K)
	m = np.float64(m)
	
	
	Tk = K*T/(K-1.5)
	wk = np.sqrt(((2.0*K - 3.0)*k_B*Tk)/(K*m))
	f = (n/(2.0*np.pi*(K*wk**2.0)**1.5)) * (Gamma(K+1)/(Gamma(K-0.5)*Gamma(1.5))) * (1.0 + (v**2)/(K*wk**2))**(-(K+1))
	
	return f 


def KappaDistCts(v,n,T,K,m,ProtonEff=1.0,dOmega=1.15*np.pi,nSpec=1.0,Tau=0.095,g=8.31e-5):
	'''
	This function outputs the expected count rate of a Kappa 
	distribution function given a temperature, density and velocity array.
	
	Inputs:
		v: Particle velocity array (m/s).
		n: Density (m^-3).
		T: Temperature (K).
		K: Kappa parameter.
		m: Particle mass (Kg).
		Eff: Efficiency for detecting the particle species in question.
		dOmega: The effective instrument field of view (sr).
		nSpec: The number of spectra used.
		Tau: Accumulation time for a single spectrum (s).
		g: Energy-geometric factor of the instrument mm^2 Ev/Ev
		
	Returns:
		Array of counts corresponding to each velocity in v.
	'''	
	f = KappaDist(v,n,T,K,m)*dOmega
	v4 = np.float64(v)**4
	A = (Tau*g*np.float64(ProtonEff)*nSpec)/20.0
	C = A*v4*f
	return C/1000.0
