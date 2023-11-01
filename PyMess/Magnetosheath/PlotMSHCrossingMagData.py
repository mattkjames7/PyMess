import numpy as np
import matplotlib.pyplot as plt
from .MSHCrossingMagData import MSHCrossingMagData
from .. import Globals
import DateTimeTools as TT

def PlotMSHCrossingMagData(Crossing,MagType='MSM',Ab=None,Minute=False,Rsm=1.42,fig=None,maps=[1,1,0,0],noxlabel=False,Res=None):
	'''
	Plots magnetometer data during the time of MSH crossing.
	
	Inputs:
		Crossing: Integer index for the crossing to get the data for.
		MagType: String to determine magnetometer data type -
			'MSM'|'MPN'|'Rotated'|'B.Bmp'
		Ab: Aberration angle of the magnetosphere in degrees; when set 
			to None, this angle is automatically calculated.
		Minute: Boolean, when True, will load minute resolution data.
		Res: Resampling interval in seconds, if set to Non, then no
			resampling is performed.
		Rsm: Distance to subsolar point of the magnetopause in Rm.
		fig: If None, then a new figure instance will be created, pass
			matplotlib.pyplot object to plot MAG data on existing figure.
		maps: Specifies location of subplot using 4 element list, tuple 
			or array [xmaps,ymaps,xmap,ymap]. xmaps and ymaps are
			integers specifying the total number of subplots in the x 
			and y directions, respectively. xmap specifies the position
			in the x direction of the current subplot, xmap=0 for the
			leftmost position, xmap=xmaps-1 for the rightmost. ymap 
			controls the y position, where ymap=0 places the subplot at
			the top of the page, ymap=ymaps-1 places it at the bottom.
		noxlabel: Boolean, removes x axis label and tick labels if True.

	
	'''
	
	#Get data function and labels
	if MagType == 'MPN':
		PlotLabels = ['$B_N$','$B_M$','$B_L$']
		DataLabels = ['BN','BM','BL']
		TwinAx = False
	else:
		PlotLabels = ['$B_x$','$B_y$','$B_z$']
		DataLabels = ['Bx','By','Bz']
		TwinAx = False


	
	#load in data
	data = MSHCrossingMagData(Crossing,MagType,Ab,Minute,Res,Rsm,MagType=MagType)

	#create a continuous time axis
	utc = np.copy(data.ut)
	neg = np.where(utc[1:] < utc[:-1])[0]
	if neg.size > 0:
		for i in range(0,neg,size):
			dd = TT.DateDifference(data.Date[neg[i]],data.date[neg[i]+1])
			utc[neg[i]+1] += 24.0*dd
			

	#create plot
	if fig is None:			
		fig = plt
		fig.figure()
	ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]),rowspan=2)
	
	colors = [[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]
	Bm = np.zeros(data.size,dtype='float32')
	for i in range(0,3):
		ax.plot(utc,data[DataLabels[i]],color=colors[i],label=PlotLabels[i],linewidth=1.0)
		Bm += data[DataLabels[i]]**2
	Bm = np.sqrt(Bm)
	ax.plot(utc,data[DataLabels[i]],color=[0.0,0.0,0.0],label='|B|',linewidth=1.0)
	ax.plot(utc,-data[DataLabels[i]],color=[0.0,0.0,0.0],linewidth=1.0)


	ax.hlines(0.0,np.nanmin(utc),np.nanmax(utc),linestyle='--',linewidth=1.0,color=[0.0,0.0,0.0])

	R = fig.axis()
	ax.axis([np.nanmin(utc),np.nanmax(utc),R[2],R[3]])
	ax.set_ylabel('Magnetic Field')
	
	OverlayMP(ax,[data.Date[0],data.Date[-1]])

	if noxlabel == False:
		TT.DTPlotLabel(ax,Seconds=True,IncludeYear=False)
		fig.xlabel('UT')
	else:
		ax.xaxis.set_visible(False)
		
	ax.legend()
	return ax
