import numpy as np
from .MaxwellBoltzmannDist import MaxwellBoltzmannDist,MaxwellBoltzmannDistCts
from scipy.optimize import minimize

def _GetMisfitFunc(v,f,df,mass=1.67212e-27):
	'''
	This function calculates the RMS misfit between the PSD and the 
	model Maxwellian distribuition PSD.
	
	Inputs:
		v: Particle velocity (m/s)
		f: Measured PSD (s^3 m^-6)
		df: Poisson error in f.
		mass: Particle mass in kg.
		
	Returns:
		RMS misfit function.
	'''
	def Func(X):
		n,T = X 
		
		fm = MaxwellBoltzmannDist(n,v,T,mass)
		
		lf = np.log10(f)
		lm = np.log10(fm)
		diff = np.sqrt(np.sum(((lf-lm)**2)/df)/f.size)
		
		return diff

	return Func

def FitMaxwellianDist(v,f,Counts,n0,T0,mass=1.67212e-27):
	'''
	This function will numerically fit a Maxwelliandistribution fuction 
	to a FIPS spectrum.
	
	Inputs:
		v: Particle velocity (m/s)
		f: Measured PSD (s^3 m^-6)
		Counts: Counts.
		n0: Initial density guess (m^-3).
		T0: Initial temperature guess (K)
		mass: Particle mass in kg.
		
	Returns:	
		Tuple containing the fitted density and temperature
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
		return -1, -1
	Func = _GetMisfitFunc(v[good],f[good],df[good],mass)
	res = minimize(Func,[n0,T0],method='nelder-mead')
	print(res.success)
	#return n,T fitted
	return res.x

		
def _GetMisfitFuncCts(v,C,dC,dOmega=1.15*np.pi,mass=1.67212e-27,ProtonEff=1.0,nSpec=1.0,Tau=0.095,g=8.31e-5):
	'''
	This function calculates the RMS misfit between the counts and the 
	model Maxwellian distribuition counts.
	
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
		n,T = X 
		
		Cm = MaxwellBoltzmannDistCts(n,v,T,mass,ProtonEff,dOmega,nSpec,Tau,g)
		
		diff = np.sqrt(np.sum(((C-Cm)**2))/C.size)
		
		return diff

	return Func

def FitMaxwellianDistCts(v,Counts,n0,T0,dOmega=1.15*np.pi,mass=1.67212e-27,ProtonEff=1.0,nSpec=1.0,Tau=0.095,g=8.31e-5):
	'''
	This function will numerically fit a Maxwellian distribution function 
	to a FIPS spectrum.
	
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
		Tuple containing the fitted density and temperature
	'''		
	#calculate error bars using Poisson statistics
	bad = np.where(np.isfinite(Counts) == False)[0]
	Counts[bad] = 0.0
	Counts1 = np.copy(Counts)
	Counts1[Counts1 < 1.0] = 1.0
	dC = np.sqrt(Counts)/Counts1
	delC = dC*Counts	

	#select only good data to fit to
	good = np.where((Counts >= 0.0))[0]
	if (good.size < 3.0):
		return -1, -1
	Func = _GetMisfitFuncCts(v[good],Counts[good],dC[good],dOmega,mass,ProtonEff,nSpec,Tau,g)
	res = minimize(Func,[n0,T0],method='nelder-mead')
	if not res.success:
		return -1,-1
	#return n,T fitted
	return res.x

