from ... import Globals
#import subprocess
import numpy as np
import DateTimeTools as TT
from ...Tools.ListFiles import ListFiles
import fnmatch as fnm

def FindPDSFiles():
	'''
	This function will search the MESSENGER_PATH/MAG/PDS directory for
	*.TAB files and list them along with their dates.
	'''
	PDSPath = Globals.MessPath+'/MAG/PDS/'
	#cmd = 'find '+Globals.MessPath+'/MAG/PDS/ -name "*.TAB"'
	files,names = ListFiles(PDSPath,True)
	matches=np.zeros(np.size(files),dtype='bool')
	for i in range(0,np.size(files)):
		if fnm.fnmatch(files[i],'*.TAB'):
			matches[i]=True	
	use = np.where(matches)[0]
	files = files[use]
	names = names[use]
	srt = np.argsort(names)
	files = files[srt]
	names = names[srt]
	
	#output = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).communicate()[0]
	#files = output.decode().split()
	#files = np.array(files)
	#files.sort()
	
	datesub = [(x.split('/')[-1])[9:14] for x in files]
	years = np.array([2000 + np.int32(x[:2]) for x in datesub])
	doys = np.array([np.int32(x[2:]) for x in datesub])
	
	dates = np.array([TT.DayNotoDate(years[i],doys[i]) for i in range(0,years.size)],dtype='int32')
	
	return files,dates
	
	
