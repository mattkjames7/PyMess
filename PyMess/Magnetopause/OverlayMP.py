import numpy as np
import DateTimeTools as TT
from .. import Globals
from .GetMPCrossings import GetMPCrossings

def OverlayMP(ax,Date,ShadeCrossings=True,UseLabel=True):
	'''
	Overlays the MP crossings on a time series plot. 
	
	Inputs:
		ax: matplotlib.pyplot.axes object.
		Date: 32-bit integer scalar or 2 element array, list or tuple in
			the format yyyymmdd to corresponding the the date(s) plotted 
			in the existing axes.
		ShadeCrossings: Boolean, if True then the area between the inner
			and outer boundaries of the MP crossings will be shaded in.
		UseLabel: Boolean, if True then a label is added for the legend.
		
		
	'''
	MPData = GetMPCrossings(Date)
	nMP = MPData.size

	if nMP > 0:
		#we will assume that the data are plotted along a ut axis in hours,
		#starting at 0 at midnight on the first day, ending at 24*No of days
		#in total. Anything outside of the plot range shouldn't show up 
		#(in theory anyway)
		ut0 = MPData.ut0
		ut1 = MPData.ut1
		StartDate = np.array([Date]).flatten()[0]
		for i in range(0,nMP):
			dd0 = TT.DateDifference(StartDate,MPData[i].Date0)
			dd1 = TT.DateDifference(StartDate,MPData[i].Date1)
			ut0[i] += dd0*24.0
			ut1[i] += dd1*24.0
			
	
		#now for plotting
		#get the plots y limits
		R = ax.axis()
		yrnge = [R[2],R[3]]
		
		#plot and optionally shade each crossing
		for i in range(0,nMP):
			if i == 0 and UseLabel:
				labelm = 'MP Crossing' 
			else:
				labelm = None
			ax.plot([ut0[i],ut0[i]],[yrnge[0],yrnge[1]],color='orange',label=labelm,linewidth=2.0)
			ax.plot([ut1[i],ut1[i]],[yrnge[0],yrnge[1]],color='orange',label=labelm,linewidth=2.0)
			if ShadeCrossings:
				ax.fill([ut0[i],ut1[i],ut1[i],ut0[i]],[yrnge[0],yrnge[0],yrnge[1],yrnge[1]],color=[1.0,0.5,0.0,0.25])
