import numpy as np
import os
from .. import Globals
import RecarrayTools as RT

dtypects = [('Date', '>i4'), ('ut', '>f4'), ('JulDay', '>f8'), ('MET', '>u4'), 
			('Orbit', '>u4'), ('AccumTime', '>u4'), ('Alt', '>f4'), ('Lat', '>f4'), 
			('Lon', '>f4'), ('LG1Raw', '>f4'), ('LG2Raw', '>f4'), ('BPRaw', '>f4'), 
			('SWTot', '>f4'), ('DeadTime', '>f4'), ('LG1Reset', '>f4'), 
			('LG2Reset', '>f4'), ('BPReset', '>f4'), ('BPPLGXS', '>f4'), 
			('LG1Over', '>f4'), ('LG2Over', '>f4'), ('BPOver', '>f4'), 
			('DoubCoin1', '>f4'), ('DoubCoin2', '>f4'), ('TripCoin', '>f4'), 
			('TCEarly', '>f4'), ('TCLate', '>f4')]

dtypegab = [('MET', '>i4'), ('Date', '>i4'), ('ut', '>f4'), ('Orbit', '>i4'),
			('GRMode', '>i4'), ('BP_UL', '>i4'), ('TrigBCAccum', '>i4'),
			('BurstThresh', '>i4'), ('PostTrigCTS', '>i4'), ('GRBurst', '>i4', (164,))]

dtypegcr = [('Date', '>i4'), ('ut', '>f4'), ('JulDay', '>f8'), ('MET', '>u4'), 
			('Orbit', '>u4'), ('AccumTime', '>u4'), ('Alt', '>f4'), ('Lat', '>f4'), 
			('Lon', '>f4'), ('GCRSpec1', '>f4', (64,)), ('GCRSpec2', '>f4', (64,))]

dtypespe = [('Date', '>i4'), ('ut', '>f4'), ('JulDay', '>f8'), ('MET', '>u4'),
			('Orbit', '>u4'), ('AccumTime', '>u4'), ('Alt', '>f4'), ('Lat', '>f4'),
			('Lon', '>f4'), ('Vnorm', '>f4'), ('Vdotx', '>f4'), ('Vdoty', '>f4'), 
			('Vdotz', '>f4'), ('NadirAngle', '>f4'), ('XaxAngle', '>f4'), 
			('YaxAngle', '>f4'), ('ThetaAngle', '>f4'), ('PhiAngle', '>f4'), 
			('BetaAngle', '>f4'), ('Rsun', '>f4'), ('Vsc', '>f4', (3,)), 
			('SCtoNadirRot', '>f4', (9,)), ('LG1Spec', '>f4', (64,)), 
			('LG2Spec', '>f4', (64,)), ('BPSpec', '>f4', (64,)), 
			('TCEarlySpec', '>f4', (256,)), ('TCLateSpec', '>f4', (256,))]

dtypencr = [('Date', '>i4'), ('ut', '>f4'), ('JulDay', '>f8'), ('MET', '>i4'), 
			('Orbit', '>i4'), ('AccumTime', '>i4'), ('SensorT', '>f8'), 
			('Alt', '>f8'), ('Lat', '>f8'), ('Lon', '>f8'), ('LT', '>f8'), 
			('Vsc', '>f8', (3,)), ('Vnorm', '>f8'), ('SCtoNadirRot', '>f8', (9,)), 
			('Vdotx', '>f8'), ('Vdoty', '>f8'), ('Vdotz', '>f8'), 
			('NadirAngle', '>f8'), ('XaxAngle', '>f8'), ('YaxAngle', '>f8'), 
			('ThetaAngle', '>f8'), ('PhiAngle', '>f8'), ('BetaAngle', '>f8'), 
			('Rsun', '>f8'), ('Counts1', '>f8'), ('CountsErr1', '>f8'), 
			('Counts2', '>f8'), ('CountsErr2', '>f8'), ('CountsBP', '>f8'), 
			('CountsErrBP', '>f8')]


nsdict = {	'cts':	('CTS/',dtypects,'NS-CTS-{:08d}.bin'),
			'gab':	('GAB/',dtypegab,'NS-GAB-{:08d}.bin'),
			'gcr':	('GCR/',dtypegcr,'NS-GCR-{:08d}.bin'),
			'spe':	('SPE/',dtypespe,'NS-SPE-{:08d}.bin'),
			'ncr':	('NCR/',dtypencr,'NS-NCR-{:08d}.bin'),}
			
def ReadNS(Date,Type='cts'):
	'''
	Reads NS data files.
	
	Inputs:
		Date: 32-bit integer date in the format yyyymmdd.
		Type: String - 'cts'|'gab'|'gcr'|'spe'|'ncr'
		
	Returns:
		numpy.recarray
	
	'''
	nspath = Globals.ModulePath
	subdir,dtype,fpatt = nsdict[Type]
	
	fname = Globals.ModulePath + subdir + fpatt.format(Date)
	
	if not os.path.isfile(fname):
		return np.recarray(0,dtype=dtype)
		
	return RT.ReadRecarray(fname,dtype)
	
