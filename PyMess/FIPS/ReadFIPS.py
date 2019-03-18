import numpy as np
import os
from .. import Globals
import RecarrayTools as RT

dtypeedr = [('MET',''),('ScanType',''),('ProtonRate','',(64,))]

dtypecdr = [('MET',''),('Date','int32')('ut','float32'),('Quality',''),('ScanType',''),('ProtonFlux','',(64,))]

dtypeespec = [('Index',''),('MET',''),('HFlux',''),('He2Flux',''),('HeFlux',''),('NaFlux',''),('OFlux','')]

dtypentp = [('StartIndex',''),('StopIndex',''),('StartMET',''),('StopMET'),('TimeRes',''),('Ion',''),('n',''),('t',''),('p',''),('nErr',''),('tErr',''),('pErr',''),('Quality','')]


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
	nspath = Globals.ModulePath
	subdir,dtype,fpatt = fipsdict[Type]
	
	fname = Globals.ModulePath + subdir + fpatt.format(Date)
	
	if not os.path.isfile(fname):
		return np.recarray(0,dtype=dtype)
		
	return RT.ReadRecarray(fname,dtype)
	
