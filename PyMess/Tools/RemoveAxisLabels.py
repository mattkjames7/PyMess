import numpy as np

def RemoveAxisLabels(ax,axis='x'):
	'''
	This function will remove the tick labels from a specific plot axis.
	
	Inputs:
		ax: pyplot.Axes instance
		axis: 'x' or 'y' string indicating which axis to remove labels 
			from
	'''
	if axis == 'y':
		lbl = ax.get_yticklabels()
		ax.set_yticklabels(['']*np.size(lbl))
	else:
		lbl = ax.get_xticklabels()
		ax.set_xticklabels(['']*np.size(lbl))
