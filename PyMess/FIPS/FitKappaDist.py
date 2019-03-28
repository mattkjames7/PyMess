import numpy as np
from .KappaDist import KappaDist,KappaDistCts
from scipy.optimize import minimize

def _GetMisfitFunc(v,f,df,mass=1.67212e-27):
	'''
	This function calculates the RMS misfit between the PSD and the 
	model Kappa distribuition PSD.
	
	Inputs:
		v: Particle velocity (m/s)
		f: Measured PSD (s^3 m^-6)
		df: Poisson error in f.
		mass: Particle mass in kg.
		
	Returns:
		RMS misfit function.
	'''
	def Func(X):
		n,T,K = X 
		
		fk = KappaDist(v,n,T,K,mass)
		#if np.isnan(fk[0]):
	#		print(n,T,K,fk)
		lf = np.log10(f)
		lk = np.log10(fk)
		diff = np.sqrt(np.sum(((lf-lk)**2)/df)/f.size)
		
		return diff

	return Func

def FitKappaDist(v,f,Counts,n0,T0,mass=1.67212e-27):
	'''
	This function will numerically fit a kappa distribution fuction to a
	FIPS spectrum.
	
	Inputs:
		v: Particle velocity (m/s)
		f: Measured PSD (s^3 m^-6)
		Counts: Counts.
		n0: Initial density guess (m^-3).
		T0: Initial temperature guess (K)
		mass: Particle mass in kg.
		
	Returns:	
		Tuple containing the fitted density, temperature and kappa
	'''
	#calculate error bars using Poisson statistics
	bad = np.where(np.isfinite(Counts) == False)[0]
	Counts[bad] = 0.0
	Counts1 = np.copy(Counts)
	Counts1[Counts1 < 1.0] = 1.0
	df = np.sqrt(Counts)/Counts1
	delF = df*f	

	#select only good data to fit to
	good = np.where(np.isfinite(f) & (Counts > 1.0))[0]
	if (good.size < 3.0):
		return -1, -1, -1
	Func = _GetMisfitFunc(v[good],f[good],df[good],mass)
	res = minimize(Func,[n0,T0,5.0],method='nelder-mead')
	print(res.success)
	#return n,T and Kappa fitted
	return res.x

def _GetMisfitFuncCts(v,C,dC,dOmega=1.15*np.pi,mass=1.67212e-27,Eff=1.0,nSpec=1.0,Tau=0.095,g=8.31e-5):
	'''
	This function calculates the RMS misfit between the counts and the 
	model Kappa distribuition counts.
	
	Inputs:
		v: Particle velocity (m/s)
		C: Counts.
		dC: Poisson error in counts.
		dOmega: Effective field of view of the instrument.
		mass: Particle mass in kg.
		Eff: Efficiency of instrument for the particle species in question.
		nSpec: The number of spectra summed to create C.
		Tau: Accumulation time for each of the nSpec(s).
		g: Energy-geometric factor of the instrument mm^2 Ev/Ev
		
	Returns:
		RMS misfit function.
	'''		
	def Func(X):
		n,T,K = X 
		
		Cm = KappaDistCts(v,n,T,K,mass,Eff,dOmega,nSpec,Tau,g)
		print('C:')
		print(Cm)
		print(C)
		
		diff = np.sqrt(np.sum(((C-Cm)**2))/C.size)

		return diff

	return Func

def FitKappaDistCts(v,Counts,n0,T0,dOmega=1.15*np.pi,mass=1.67212e-27,Eff=1.0,nSpec=1.0,Tau=0.095,g=8.31e-5):
	'''
	This function will numerically fit a kappa distribution fuction to a
	FIPS spectrum.
	
	Inputs:
		v: Particle velocity (m/s)
		Counts: Counts.
		n0: Initial density guess (m^-3).
		T0: Initial temperature guess (K)
		dOmega: Effective field of view of the instrument.
		mass: Particle mass in kg.
		Eff: Efficiency of instrument for the particle species in question.
		nSpec: The number of spectra summed to create C.
		Tau: Accumulation time for each of the nSpec(s).
		g: Energy-geometric factor of the instrument mm^2 Ev/Ev
				
	Returns:	
		Tuple containing the fitted density, temperature and kappa
	'''	
	#calculate error bars using Poisson statistics
	bad = np.where(np.isfinite(Counts) == False)[0]
	Counts[bad] = 0.0
	Counts1 = np.copy(Counts)
	Counts1[Counts1 < 1.0] = 1.0
	dC = np.sqrt(Counts)/Counts1
	delC = dC*Counts	
	dC[dC == 0.0] = 1.0e-40

	#select only good data to fit to
	if np.size(Eff) == 1:
		Eff = np.array([Eff]*64).flatten()
	
	good = np.where((Counts >= 0.0) & np.isfinite(Eff))[0]
	if (good.size < 3.0):
		return -1, -1 -1

	Func = _GetMisfitFuncCts(v[good],Counts[good],dC[good],dOmega,mass,Eff[good],nSpec,Tau,g)
	res = minimize(Func,[n0,T0,130.0],method='nelder-mead')
	if not res.success:
		return -1, -1, -1
	#return n,T fitted
	return res.x
		
