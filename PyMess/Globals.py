import os
ModulePath = os.path.dirname(__file__)+'/'
try:
	MessPath = os.getenv('MESSENGER_PATH')+'/'
except:
	print('Please set MESSENGER_PATH environment variable')
	MessPath = ''

#Store loaded MAG data in memory for quick access
LoadedMAGData = {}
LoadedMAGRotatedData = {}
MagRes = None

#Magnetopause and bow shock crossings
MPData = None
BSData = None

#SW times
SWTimes = None

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

#FIPS dtypes
fips60sdtype = [('Date','int32'),('ut','float32'),('MET','float64'),('StartMET','float64'),('StopMET','float64'),('StartIndex','int32'),('StopIndex','int32'),('ScanType','int8'),
				('NSpec','int32'),('Tau','float32'),('CDRQuality','int16',(7,)),('Ion','U3',(5,)),('Mass','float32',(5,)),('HasNTP','bool8',(5,)),('EQBins','float32',(64,)),
				('Efficiency','float32',(5,64)),('VBins','float32',(5,64)),('Counts','float32',(5,64)),('Flux','float32',(5,64,)),('PSD','float32',(5,64,)),
				('n','float32',(5,)),('t','float32',(5,)),('p','float32',(5,)),('nk','float32',(5,)),('tk','float32',(5,)),('pk','float32',(5,)),('k','float32',(5,))]
