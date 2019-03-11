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

#FIPS data
FIPSProtEff = None
FIPSData = None


#orbits
Orbits = None

#field line traces
Traces = {}

#MESSENGER location
Position = None
MercurySpeed = None
AberrationAngle = {}

