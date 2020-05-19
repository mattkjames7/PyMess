import os
import numpy as np
ModulePath = os.path.dirname(__file__)+'/'
ModuleData = os.path.dirname(__file__)+'/__data/'
try:
	MessPath = os.getenv('TEST_MESSENGER_PATH')+'/'
except:
	print('Please set TEST_MESSENGER_PATH environment variable')
	MessPath = ''
	
#mission elapsed time
MET = None

#Store loaded MAG data in memory for quick access
LoadedMAGData = {}
LoadedMAGRotatedData = {}
MagRes = None

#Magnetopause and bow shock crossings
MPData = None
BSData = None

#SW times
SWTimes = None

#MSTimes
MSTimes = None

#MSH times
MSHTimes = None

#FIPS data
FIPSProtEff = None
FIPSData = None


#orbits
Orbits = None

#field line traces
Traces = {}

#MESSENGER location
Position = None

#Mercury location
MercuryPos = None
MercurySpeed = None
AberrationAngle = {}

#E/Q bin energies (ev) - EQBins[ScanType] provides the correct energy range
bins2 = np.array([  13.577,  12.332,  11.201,  10.174,   9.241,   8.393,
					 7.623,   6.924,   6.289,   5.712,   5.188,   4.713,   4.28 ,
					 3.888,   3.531,   3.207,   2.913,   2.646,   2.403,   2.183,
					 1.983,   1.801,   1.636,   1.485,   1.349,   1.225,   1.113,
					 1.011,   0.918,   0.834,   0.758,   0.688,   0.625,   0.568,
					 0.516,   0.468,   0.426,   0.386,   0.351,   0.319,   0.29 ,
					 0.263,   0.239,   0.217,   0.197,   0.179,   0.163,   0.148,
					 0.134,   0.122,   0.111,   0.1  ,   0.046,   0.046,   0.046,
					 0.046,   0.046,   0.046,   0.046,   0.046,   0.046,   0.046,
					 0.046,   0.046])	

bins0 = np.array([  13.577,  12.332,  11.201,  10.174,   9.241,   8.393,
					 7.623,   6.924,   6.289,   5.712,   5.188,   4.713,   4.28 ,
					 3.888,   3.531,   3.207,   2.913,   2.646,   2.403,   2.183,
					 1.983,   1.801,   1.636,   1.485,   1.349,   1.225,   1.113,
					 1.011,   0.918,   0.834,   0.758,   0.688,   0.625,   0.568,
					 0.516,   0.468,   0.426,   0.386,   0.351,   0.319,   0.29 ,
					 0.263,   0.239,   0.217,   0.197,   0.179,   0.163,   0.148,
					 0.134,   0.122,   0.111,   0.1  ,   0.091,   0.083,   0.075,
					 0.068,   0.062,   0.056,   0.051,   0.046,   0.046,   0.046,
					 0.046,   0.046])


EQBins = {	0:	bins0,
			2:	bins2}

#Tau
Tau = {	0:	0.095,
		2:	0.005}
		
#Ion Mass
IonMass = { 'H': 	1.007,
			'He':	4.0026,
			'Na':	22.9898,
			'O':	15.999}

class Constants(object):
	e = 1.6022e-19
	amu = 1.6605e-27
	dOmega = 1.15*np.pi
	g = 8.31e-5
	kB = 1.38064852e-23

#FIPS dtypes
dtype60s = [('Date','int32'),				#Date in format yyyymmdd
			('ut','float32'),				#UT time since begining of day in hours
			('MET','float64'),				#Mission elapsed time
			('StartMET','float64'),			#Start MET of observation
			('StopMET','float64'),			#End MET of observation
			('StartIndex','int32'),			#Start index
			('StopIndex','int32'),			#end index
			('ScanType','int8'),			#Scan Type is either 0 or 2 to determine energy bin ranges
			('NSpec','int32'),				#Number of spectra combined 
			('Tau','float32'),				#Tau parameter - dwell time on each energy bin
			('CDRQuality','int16',(7,)),	#CDR data quality flag (0 = good, I think)
			('NTPQuality','int16'),			#NTP data quality flag (0 = good)
			('Ion','U3'),					#Species of ion
			('HasNTP','bool8'),				#Whether this spectrum has an NTP fit
			('EQBins','float32',(64,)),		#Energy/charge bins in keV/Q
			('Efficiency','float32',(64,)),	#Efficiency parameter (rho) - carful, I worked backwards to get this so it may be wrong!
			('VBins','float32',(64,)),		#Velocity bins in km/s
			('Counts','float32',(64,)),		#Measured counts for each energy bin
			('Flux','float32',(64,)),		#Differential energy flux in (keV/e)^-1 s^-1 cm^-2 sr^-1 calculated from the count rate in  (this is directly taken from PDS, I didn't do this)
			('PSD','float32',(64,)),		#Phase space density in s^3 m^-6 calculated from the flux
			('n','float32'),				#Maxwellian density in cm^-3 from NTP
			('t','float32'),				#Maxwellian temperature in MK from NTP
			('p','float32'),				#Maxwellian pressure in nPa from NTP
			('nk','float32'),				#Kappa density in cm^-3 from James et al 2020
			('tk','float32'),				#Kappa temperature in MK from James et al 2020
			('pk','float32'),				#Kappa pressure in nPa from James et al 2020
			('k','float32'),					#Kappa parameter from James et al 2020
			('SplitProb','float32',(8,)),	#ANN output probabilities that each section is good
			('Prob','float32'),				#ANN probability that whole spectrum is good fit
			('SplitClass','int8',(8,)),		#Classification of each section (1 = good, 0 = bad, -1 = not classififed)
			('Class','int8')]				#Classification of whole spectrum (1 = good, 0 = bad, -1 = not classified)

dtype10s = [('Date','int32'),
			('ut','float32'),
			('MET','float64'),
			('StartIndex','int32'),
			('ScanType','int8'),
			('Tau','float32'),
			('CDRQuality','int16'),
			('NTPQuality','int16'),
			('Ion','U3'),
			('HasNTP','bool8'),
			('EQBins','float32',(64,)),
			('Efficiency','float32',(64,)),
			('VBins','float32',(64,)),
			('Counts','float32',(64,)),
			('Flux','float32',(64,)),
			('PSD','float32',(64,)),
			('n','float32'),
			('t','float32'),
			('p','float32'),
			('nk','float32'),
			('tk','float32'),
			('pk','float32'),
			('k','float32')]
			

