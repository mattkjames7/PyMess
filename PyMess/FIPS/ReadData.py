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

dtypeann = [	('Date','int32'),
				('ut','float32'),
				('nk','float32'),
				('tk','float32'),
				('K','float32'),
				('SplitProb','float32',(8,)),
				('Prob','float32'),
				('SplitClass','int8',(8,)),
				('Class','int8')]			
			
fipsdict = {'edr':		('EDR/',dtypeedr,'FIPS-EDR-{:08d}.bin'),
			'cdr':		('CDR/',dtypecdr,'FIPS-CDR-{:08d}.bin'),
			'espec':	('ESPEC/',dtypeespec,'FIPS-ESPEC-{:08d}.bin'),
			'ntp':		('NTP/',dtypentp,'FIPS-NTP-{:08d}.bin'),
			'ann':		('ANN/bin/',dtypeann,'{:08d}.bin'),
			'60H':		('Combined/60s/H/',Globals.dtype60s,'{:08d}.bin'),
			'60He':		('Combined/60s/He/',Globals.dtype60s,'{:08d}.bin'),
			'60He2':	('Combined/60s/He2',Globals.dtype60s,'{:08d}.bin'),
			'60Na':		('Combined/60s/Na/',Globals.dtype60s,'{:08d}.bin'),
			'60O':		('Combined/60s/O/',Globals.dtype60s,'{:08d}.bin'),
			'10H':		('Combined/10s/H/',Globals.dtype10s,'{:08d}.bin'),}
			
def ReadData(Date,Type='60H',Length=False):
	'''
	Reads FIPS data files.
	
	Inputs:
		Date: 32-bit integer date in the format yyyymmdd.
		Type: String - 'edr'|'cdr'|'espec'|'ntp'|'ann'|'60H'|'60He'|
			'60He2'|'60Na'|'60O'|'10H',	default is '60H' which 
			corresponds to the 60s combined data.
	Length : bool
		If True, then only the length of the data file is returned, 
		otherwise the whole file is read in.
		
	Returns:
		numpy.recarray
	
	'''
	subdir,dtype,fpatt = fipsdict[Type]
	
	fname = Globals.MessPath + 'FIPS/' + subdir + fpatt.format(Date)
	if not os.path.isfile(fname):
		print('File not found: '+fname)
		if Length:
			return 0
		else:
			return np.recarray(0,dtype=dtype)
	
	if Length:
		f = open(fname,'rb')
		l = np.fromfile(f,dtype='int32',count=1)[0]
		f.close()
		return l
	else:
		return RT.ReadRecarray(fname,dtype)
	
