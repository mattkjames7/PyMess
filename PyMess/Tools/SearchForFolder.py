from .ListDirectories import ListDirectories
import numpy as np

def SearchForFolder(infolder,name):
	'''
	Searched for a folder name somwhere within another folder.
	
	'''
	dirs,names = ListDirectories(infolder,True)
	
	use = np.where(names == name)[0]
	return dirs[use]
	
