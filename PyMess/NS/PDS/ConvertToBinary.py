import numpy as np
from .FindPDSFiles import FindPDSFiles
from ...Tools.ReadPDSFile import ReadPDSFile
import RecarrayTools as RT
from ... import Globals
from ...Tools.PDSFMTtodtype import PDSFMTtodtype
import DateTimeTools as TT

ctsfields = {	'UTC_TIME':				('Date','ut'),
				'UTC_TIME_JULDAY':  	'JulDay',
				'MISSION_ELAPSED_TIME':	'MET',
				'ORBIT_NUMBER':			'Orbit',
				'ACTUAL_ACCUM':			'AccumTime',
				'SC_ALTITUDE':			'Alt',
				'SC_LATITUDE':			'Lat',
				'SC_LONGITUDE':			'Lon',
				'LG1_RAW_EVENTS':		'LG1Raw',
				'LG2_RAW_EVENTS':		'LG2Raw',
				'BS_RAW_EVENTS':		'BPRaw',
				'SW_TOTAL_EVENTS':		'SWTot',
				'DEAD_TIME':			'DeadTime',
				'LG1_RESET':			'LG1Reset',
				'LG2_RESET':			'LG2Reset',
				'BP_RESET':				'BPReset',
				'BPP_LGXS':				'BPPLGXS',
				'LG1_OVER_RANGE': 		'LG1Over',
				'LG2_OVER_RANGE': 		'LG2Over',
				'BP_OVER_RANGE': 		'BPOver',
				'LG1_BPP_COIN':			'DoubCoin1',
				'LG2_BPP_COIN':			'DoubCoin2',
				'LG1_BPP_LG1_COIN':		'TripCoin',
				'TC_EARLY':				'TCEarly',
				'TC_LATE':				'TCLate'}


gabfields = {	'MET':					'MET',
				'CMD_UTC_DATE':			('Date',),
				'CMD_UTC_TIME':			('ut',),
				'ORBIT_NUMBER':			'Orbit',
				'GAMMA_RAY_MODE':		'GRMode',
				'BP_CH_UPPER_LIMIT':	'BP_UL',
				'TRIG_BOXCAR_ACCUM':	'TrigBCAccum',
				'BURST_THRESHOLD':		'BurstThresh',
				'POST_TRIGGER_COUNTS':	'PostTrigCTS',
				'GAMMA_RAY_BURST':		'GRBurst'}
				
	
gcrfields = {	'UTC_TIME':				('Date','ut'),
				'UTC_TIME_JULDAY':  	'JulDay',
				'MISSION_ELAPSED_TIME':	'MET',
				'ORBIT_NUMBER':			'Orbit',
				'ACTUAL_ACCUM':			'AccumTime',
				'SC_ALTITUDE':			'Alt',
				'SC_LATITUDE':			'Lat',
				'SC_LONGITUDE':			'Lon',		
				'LG1_GCR_SPECTRA':		'GCRSpec1',
				'LG2_GCR_SPECTRA':		'GCRSpec2'}

spefields = {	'UTC_TIME':				('Date','ut'),
				'UTC_TIME_JULDAY':  	'JulDay',
				'MISSION_ELAPSED_TIME':	'MET',
				'ORBIT_NUMBER':			'Orbit',
				'ACTUAL_ACCUM':			'AccumTime',
				'SC_ALTITUDE':			'Alt',
				'SC_LATITUDE':			'Lat',
				'SC_LONGITUDE':			'Lon',
				'VEL_NORM':				'Vnorm',
				'V_DOT_X':				'Vdotx',
				'V_DOT_Y':				'Vdoty',
				'V_DOT_Z':				'Vdotz',
				'NADIR_ANGLE':			'NadirAngle',
				'XAXIS_ANGLE':			'XaxAngle',
				'YAXIS_ANGLE':			'YaxAngle',
				'THETA_ANGLE':			'ThetaAngle',
				'PHI_ANGLE':			'PhiAngle',
				'BETA_ANGLE':			'BetaAngle',
				'SUN_DISTANCE':			'Rsun',
				'VEL_VECTOR':			'Vsc',
				'SC_TO_NADIR_ROT':		'SCtoNadirRot',
				'LG1_SPECTRA':			'LG1Spec',
				'LG2_SPECTRA':			'LG2Spec',
				'BP_SPECTRA':			'BPSpec',
				'TC_EARLY_SPECTRA':		'TCEarlySpec',
				'TC_LATE_SPECTRA':		'TCLateSpec'}
		
ncrfields = {	'UTC_TIME':				('Date','ut'),
				'JULIAN_DAY':  			'JulDay',
				'MET':					'MET',
				'ORBIT_NUMBER':			'Orbit',
				'ACTUAL_ACCUM':			'AccumTime',
				'SENSOR_TEMP':			'SensorT',
				'ALTITUDE':				'Alt',
				'LATITUDE':				'Lat',
				'LONGITUDE':			'Lon',				
				'LOCAL_TIME':			'LT',
				'VELOCITY_VECTOR':		'Vsc',
				'VEL_NORM':				'Vnorm',
				'SC_TO_NADIR_ROT':		'SCtoNadirRot',
				'VDOT_X':				'Vdotx',
				'VDOT_Y':				'Vdoty',
				'VDOT_Z':				'Vdotz',
				'NADIR_ANGLE':			'NadirAngle',
				'XAXIS_ANGLE':			'XaxAngle',
				'YAXIS_ANGLE':			'YaxAngle',
				'THETA_ANGLE':			'ThetaAngle',
				'PHI_ANGLE':			'PhiAngle',
				'BETA_ANGLE':			'BetaAngle',
				'SUN_DISTANCE':			'Rsun',		
				'LG1_CPS':				'Counts1',	
				'LG1_ERR_CPS':			'CountsErr1',	
				'LG2_CPS':				'Counts2',	
				'LG2_ERR_CPS':			'CountsErr2',	
				'BP_CPS':				'CountsBP',	
				'BP_ERR_CPS':			'CountsErrBP'}	

def ConvertToBinary():
	
	#set the NS path
	nspath = Globals.MessPath+'NS/'
	
	#get the lists of files
	nspds = FindPDSFiles()

	#set the fname pattern
	fpatts = ['NS-CTS-{:08d}.bin','NS-GAB-{:08d}.bin','NS-GCR-{:08d}.bin','NS-SPE-{:08d}.bin','NS-NCR-{:08d}.bin']
	
	#list the fields to keep and their new names
	allfields = [ctsfields,gabfields,gcrfields,spefields,ncrfields]
	
	#list the 5 products
	Prods = ['cts','gab','gcr','spe','ncr']


	#now loop through converting each product
	for i in range(0,5):
		print('Converting Product: {:s} ({:d}/{:d})'.format(Prods[i],i+1,5))
		
		fmt,files,outdir = nspds[Prod[i]]
		field = allfields[i]
		
		_ConvBinary(fmt,files,outdir,fpatts[i],field)
		
		
def _NewDtype(pdsdata,fields):
	
	oldfields = list(fields.keys())
	
	newdtype = []
	
	for f in oldfields:
		sh = pdsdata[f].dtype.shape
		if len(sh) == 0:
			tmp = (fields[f],pdsdata[f].dtype.str)
		else:
			tmp = (fields[f],pdsdata[f].dtype.str,pdsdata[f].dtype.shape)
		newdtype.append(tmp)
	return newdtype
		
		

def _ConvBinary(fmt,files,outdir,fpatt,fields):
	#set the output folder
	outpath = Globals.MessPath+'NS/'+outdir
	

	
	#get fmt data
	fmtdata = PDSFMTtodtype(fmt)
	
	
	oldfields = list(fields.keys())
	newfields = [fields[f] for f in oldfields]
	
	
	#loop through files
	nf = np.size(files)
	for i in range(0,nf):
		print('\rConverting file {:d} of {:d}'.format(i+1,nf),end='')
		
		#get the date from the file name
		fsplit = files[i].split('/')
		flast = fsplit[-1]
		year = np.int32(flast[10:14])
		doy = np.int32(flast[14:17])
		Date = TT.DayNotoDate(year,doy)
		
		#read the file first
		data = ReadPDSFile(files[i],fmtdata)
		
		#get the new dtype if needed
		if i == 0:
			dtype = _NewDtype(data,fields)
		
		#get the output recarray
		out = np.recarray(data.size,dtype=dtype)
		
		#move data to new recarray
		for f in oldfields:
			out[fields[f]] = data[f]
			
		#save the file
		fname = outpath + fpatt.format(Date)
		RT.SaveRecarray(data,fname)
		
	print()
	print('dtype: ',dtype)

