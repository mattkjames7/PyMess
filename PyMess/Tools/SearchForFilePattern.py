from .ListFiles import ListFiles
import numpy as np
import fnmatch as fnm


def SearchForFilePattern(infolder,pattern):
	'''
	Searched for a file name pattern somwhere within another folder.
	
	'''
	files,names = ListFiles(infolder,True)

	matches = np.zeros(np.size(names),dtype='bool')
	for i in range(0,np.size(names)):
		if fnm.fnmatch(names[i],pattern):
			matches[i] = True
	
	use = np.where(matches)[0]
	return files[use]
	
