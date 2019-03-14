from .ListFiles import ListFiles
import numpy as np

def SearchForFile(infolder,name):
	'''
	Searched for a file name somwhere within another folder.
	
	'''
	files,names = ListFiles(infolder,True)
	
	use = np.where(names == name)[0]
	return files[use]
	
