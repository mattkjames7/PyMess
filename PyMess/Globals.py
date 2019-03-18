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
fips60sdtype = [('Date','int32'),('ut','float32'),('MET','float64'),('StartMET','float64'),('StopMET','float64'),('StartIndex','int32'),('StopIndex','int32'),
				('ScanType','int8'),('NSpec','int32'),('CDRQuality','int16',(7,)),('HasNTP','bool8',(5,)),('Tau','float32'),('Efficiency','float32',(5,)),('EQBins','float32',(64,)),
				('VBinsH','float32',(64,)),('VBinsHe2','float32',(64,)),('VBinsHe','float32',(64,)),('VBinsNa','float32',(64,)),('VBinsO','float32',(64,)),
				('HCounts','float32',(64,)),('He2Counts','float32',(64,)),('HeCounts','float32',(64,)),('NaCounts','float32',(64,)),('OCounts','float32',(64,)),
				('Hflux','float32',(64,)),('He2flux','float32',(64,)),('Heflux','float32',(64,)),('Naflux','float32',(64,)),('Oflux','float32',(64,)),
				('HPSD','float32',(64,)),('He2PSD','float32',(64,)),('HePSD','float32',(64,)),('NaPSD','float32',(64,)),('OPSD','float32',(64,)),
				('nH','float32'),('tH','float32'),('pH','float32'),('nkH','float32'),('tkH','float32'),('pkH','float32'),('kH','float32'),
				('nHe2','float32'),('tHe2','float32'),('pHe2','float32'),('nkHe2','float32'),('tkHe2','float32'),('pkHe2','float32'),('kHe2','float32'),
				('nHe','float32'),('tHe','float32'),('pHe','float32'),('nkHe','float32'),('tkHe','float32'),('pkHe','float32'),('kHe','float32'),
				('nNa','float32'),('tNa','float32'),('pNa','float32'),('nkNa','float32'),('tkNa','float32'),('pkNa','float32'),('kNa','float32'),
				('nO','float32'),('tO','float32'),('pO','float32'),('nkO','float32'),('tkO','float32'),('pkO','float32'),('kO','float32'),]
