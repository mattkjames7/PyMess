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
dtype60s = [('Date','int32'),('ut','float32'),('MET','float64'),
			('StartMET','float64'),('StopMET','float64'),
			('StartIndex','int32'),('StopIndex','int32'),
			('ScanType','int8'),
			('NSpec','int32'),('Tau','float32'),
			('CDRQuality','int16',(7,)),('NTPQuality','int16'),
			('Ion','U3'),('HasNTP','bool8'),('EQBins','float32',(64,)),
			('Efficiency','float32',(64,)),('VBins','float32',(64,)),
			('Counts','float32',(64,)),('Flux','float32',(64,)),('PSD','float32',(64,)),
			('n','float32'),('t','float32'),('p','float32'),
			('nk','float32'),('tk','float32'),('pk','float32'),('k','float32')]

dtype10s = [('Date','int32'),('ut','float32'),('MET','float64'),
			('StartIndex','int32'),
			('ScanType','int8'),
			('Tau','float32'),
			('CDRQuality','int16'),('NTPQuality','int16'),
			('Ion','U3'),('HasNTP','bool8'),('EQBins','float32',(64,)),
			('Efficiency','float32',(64,)),('VBins','float32',(64,)),
			('Counts','float32',(64,)),('Flux','float32',(64,)),('PSD','float32',(64,)),
			('n','float32'),('t','float32'),('p','float32'),
			('nk','float32'),('tk','float32'),('pk','float32'),('k','float32')]
			
fips60sdtype = [('Date','int32'),('ut','float32'),('MET','float64'),('StartMET','float64'),('StopMET','float64'),('StartIndex','int32'),('StopIndex','int32'),('ScanType','int8'),
				('NSpec','int32'),('Tau','float32'),('CDRQuality','int16',(7,)),('Ion','U3',(5,)),('Mass','float32',(5,)),('HasNTP','bool8',(5,)),('EQBins','float32',(64,)),
				('Efficiency','float32',(5,64)),('VBins','float32',(5,64)),('Counts','float32',(5,64)),('Flux','float32',(5,64,)),('PSD','float32',(5,64,)),
				('n','float32',(5,)),('t','float32',(5,)),('p','float32',(5,)),('nk','float32',(5,)),('tk','float32',(5,)),('pk','float32',(5,)),('k','float32',(5,))]
fips10sdtype = [('Date','int32'),('ut','float32'),('MET','float64'),('StartMET','float64'),('StopMET','float64'),('StartIndex','int32'),('StopIndex','int32'),('ScanType','int8'),
				('NSpec','int32'),('Tau','float32'),('CDRQuality','int16',(7,)),('Ion','U3',(5,)),('Mass','float32',(5,)),('HasNTP','bool8',(5,)),('EQBins','float32',(64,)),
				('Efficiency','float32',(5,64)),('VBins','float32',(5,64)),('Counts','float32',(5,64)),('Flux','float32',(5,64,)),('PSD','float32',(5,64,)),
				('n','float32',(5,)),('t','float32',(5,)),('p','float32',(5,)),('nk','float32',(5,)),('tk','float32',(5,)),('pk','float32',(5,)),('k','float32',(5,))]
