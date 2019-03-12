import numpy as np
import DateTimeTools as TT


def DTPlotLabel(fig,ut,date,Seconds=False,IncludeYear=True):
	'''
	Converts x-axis labels on a plot to date and time labels.
	
	Inputs:
		fig: Either matplotlib.pyplot object, or matplotlib.pyplot.axes
			object currently in use
		ut: UT values used for plotting (in hours e.g. 23.75 == 23:45).
		date: Date values for each UT value, integers in format yyyymmdd
		Seconds: Boolean, True to display seconds.
		IncludeYear: Boolean, True to show year on tick labels.
	'''
	
	if hasattr(fig,'gca'):
		ax=fig.gca()
	else:
		ax = fig
		
	mt=ax.xaxis.get_majorticklocs()
	labels=np.zeros(mt.size,dtype='U20')
	Months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	for i in range(0,mt.size):
		dt = np.abs(mt[i] - ut)
		ind = np.where(dt == np.min(dt))[0]
		datei = date[ind]
		
		yr,mn,dy = TT.DateSplit(datei)
		datestr = '{:02d} '.format(np.int(dy[0]))+Months[mn[0]-1]
		if IncludeYear:
			datestr += ' {:04d}'.format(yr[0])
		tmod = mt[i] % 24.0
		hh,mm,ss,ms=TT.DectoHHMM(tmod,True,True,True)
		if Seconds:
			utstr='{:02n}:{:02n}:{:02n}'.format(hh,mm,ss)
		else:
			if ss >= 30:
				mm+=1
				ss = 0
			if mm > 59:
				hh+=1
				mm=0
			if hh > 23:
				hh = 0
			utstr='{:02n}:{:02n}'.format(hh,mm)
		labels[i]=utstr+'\n'+datestr

	R = fig.axis()
	use = np.where((mt >= R[0]) & (mt < R[1]))[0]
	ax.set_xticks(mt[use])
	ax.set_xticklabels(labels[use])
