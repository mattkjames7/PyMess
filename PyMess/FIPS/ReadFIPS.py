import numpy as np
import os
from .. import Globals
import RecarrayTools as RT

dtypeedr = [('MET','>u4'),('ScanType','>u2'),('ProtonRate','>u4',(64,))]

dtypecdr = [('MET','>f8'),('Date','>i4'),('ut','>f4'),('Quality','>i4'),
			('ScanType','>i4'),('ProtonFlux','>f8',(64,))]

dtypeespec = [('Index', '>i4'), ('MET', '>f8'), ('HFlux', '>f8', (64,)), 
				('He2Flux', '>f8', (64,)), ('HeFlux', '>f8', (64,)), 
				('NaFlux', '>f8', (64,)), ('OFlux', '>f8', (64,))]

dtypentp = [('StartIndex', '>i4'), ('StopIndex', '>i4'), ('StartMET', '>f8'), 
			('StopMET', '>f8'), ('TimeRes', '>U16'), ('Ion', '>U16'), 
			('n', '>f8'), ('t', '>f8'), ('p', '>f8'), ('nErr', '>f8'), 
			('tErr', '>f8'), ('pErr', '>f8'), ('Quality', '>i4')]
			
			
fipsdict = {'edr':		('EDR/',dtypeedr,'FIPS-EDR-{:08d}.bin'),
			'cdr':		('CDR/',dtypecdr,'FIPS-CDR-{:08d}.bin'),
			'espec':	('ESPEC/',dtypeespec,'FIPS-ESPEC-{:08d}.bin'),
			'ntp':		('NTP/',dtypentp,'FIPS-NTP-{:08d}.bin')}
			
def ReadFIPS(Date,Type='ntp'):
	'''
	Reads FIPS data files.
	
	Inputs:
		Date: 32-bit integer date in the format yyyymmdd.
		Type: String - 'edr'|'cdr'|'espec'|'ntp'
		
	Returns:
		numpy.recarray
	
	'''
	subdir,dtype,fpatt = fipsdict[Type]
	
	fname = Globals.MessPath + 'FIPS/' + subdir + fpatt.format(Date)
	print(os.path.isfile(fname))
	if not os.path.isfile(fname):
		return np.recarray(0,dtype=dtype)
		
	return RT.ReadRecarray(fname,dtype)
	
