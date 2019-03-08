import numpy as np
import matplotlib.pyplot as plt
from .GetPosition import GetPosition
import DateTimeTools as TT
from scipy.interpolate import InterpolatedUnivariateSpline


def PlotOrbit(Date,ut,Range=[-3,3],Center=[0.0,0.0,0.0],PlanetAlpha=0.5,ShowHours=0,ShowDates=True):
	
	fig = plt
	fig.figure(figsize=(12,5))
	
	ax0 = PlotOrbitPlane(Date,ut,'XZ',Range,Center,fig,[3,1,0,0],PlanetAlpha,ShowHours,ShowDates) 
	ax1 = PlotOrbitPlane(Date,ut,'YZ',Range,Center,fig,[3,1,1,0],PlanetAlpha,ShowHours,ShowDates) 
	ax2 = PlotOrbitPlane(Date,ut,'YX',Range,Center,fig,[3,1,2,0],PlanetAlpha,ShowHours,ShowDates) 
	fig.tight_layout()
	return fig

def PlotOrbitPlane(Date,ut,Plane='XZ',Range=[-3,3],Center=[0.0,0.0,0.0],fig=None,maps=[1,1,0,0],PlanetAlpha=0.5,ShowHours=0,ShowDates=True,ShowMP=True,Rss=1.42):
	
	#read in the position data first
	data = GetPosition(Date)
	if np.size(Date) == 1:
		Date = np.array([Date,Date])
		use = np.where((data.ut >= ut[0]) & (data.ut <= ut[1]))[0]
	else:
		use = np.where(((data.Date == Date[0]) & (data.ut >= ut[0])) | ((data.Date > Date[0]) & (data.Date < Date[1])) | ((data.Date == Date[1]) & (data.ut <= ut[1])))[0]
	data = data[use]
	
	
	#decide what to plot (plotx,ploty,xlabel,ylabel,xrange,yrange,othercoord,planetcoords)
	planes = {	'XY': (data.x, data.y, 'X MSM ($R_M$)', 'Y MSM ($R_M$)',[Range[0]-Center[0],Range[1]-Center[0]],[Range[0]-Center[1],Range[1]-Center[1]], data.z+0.19,[0.0,0.0]),
				'YX': (data.y, data.x, 'Y MSM ($R_M$)', 'X MSM ($R_M$)',[Range[1]-Center[1],Range[0]-Center[1]],[Range[0]-Center[0],Range[1]-Center[0]], data.z+0.19,[0.0,0.0]),
				'YZ': (data.y, data.z, 'Y MSM ($R_M$)', 'Z MSM ($R_M$)',[Range[0]-Center[1],Range[1]-Center[1]],[Range[0]-Center[2],Range[1]-Center[2]], data.x,[0.0,-0.19]),
				'ZY': (data.z, data.y, 'Z MSM ($R_M$)', 'Y MSM ($R_M$)',[Range[0]-Center[2],Range[1]-Center[2]],[Range[0]-Center[1],Range[1]-Center[1]], data.x,[-0.19,0.0]),
				'XZ': (data.x, data.z, 'X MSM ($R_M$)', 'Z MSM ($R_M$)',[Range[0]-Center[0],Range[1]-Center[0]],[Range[0]-Center[2],Range[1]-Center[2]], data.y,[0.0,-0.19]),
				'ZX': (data.z, data.x, 'Z MSM ($R_M$)', 'X MSM ($R_M$)',[Range[1]-Center[2],Range[0]-Center[2]],[Range[0]-Center[0],Range[1]-Center[0]], data.y,[-0.19,0.0]),}
	px,py,xlabel,ylabel,xrnge,yrnge,pz,mcenter = planes[Plane]

	#initialize plot
	if fig is None:
		fig = plt
		fig.figure()
	ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
	ax.axis([xrnge[0],xrnge[1],yrnge[0],yrnge[1]])
	ax.set_aspect(1.0)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	
	#sort out zorders so that 
	zorders = np.float32((pz > 0.0) | (np.sqrt((px-mcenter[0])**2 + (py-mcenter[1])**2) > 1.0))*2.0 - 1.0
	dz = np.where(zorders[1:] != zorders[:-1])[0] + 1
	dz = np.concatenate(([0],dz,[zorders.size]))
	ndz = np.size(dz)-1
	
	#plot based on the different zorders
	for i in range(0,ndz):
		ax.plot(px[dz[i]:dz[i+1]],py[dz[i]:dz[i+1]],color=[1.0,0.5,0.0],zorder=zorders[dz[i]],linewidth=2.0)
		
	#plot the planet
	a = np.pi*np.arange(361)/180.0
	mx = np.sin(a) + mcenter[0]
	my = np.cos(a) + mcenter[1]
	ax.fill(mx[:-1],my[:-1],color=[1.0,1.0,1.0,PlanetAlpha],zorder=0.0)
	ax.plot(mx,my,color=[0.0,0.0,0.0],zorder=0.1,linewidth=2.0)
		
	#plot x=0 and y=0
	ax.plot([0.0,0.0],yrnge,color=[0.0,0.0,0.0],linestyle='--',linewidth=1.0)
	ax.plot(xrnge,[0.0,0.0],color=[0.0,0.0,0.0],linestyle='--',linewidth=1.0)
		
	#show labels wiith hours/dates
	if ShowHours > 0:
		uthr = [np.ceil(ut[0]/ShowHours)*ShowHours,np.floor(ut[1]/ShowHours)*ShowHours]
		ddate = TT.DateDifference(Date[0],Date[1])
		uthr[1] += ddate*24.0
		
		utcont = np.copy(data.ut)
		diffdate = np.where(data.Date[:-1] != data.Date[1:])[0]
		if diffdate.size > 0:
			for i in range(0,diffdate.size):
				dd = TT.DateDifference(data.Date[diffdate[i]],data.Date[diffdate[i]+1])
				utcont[diffdate[i]+1:] += 24.0*dd
				
		fx = InterpolatedUnivariateSpline(utcont,px)
		fy = InterpolatedUnivariateSpline(utcont,py)
		fz = InterpolatedUnivariateSpline(utcont,pz)
		
		uthours = np.arange((uthr[1]-uthr[0])/ShowHours)*ShowHours + uthr[0]
		hx = fx(uthours)
		hy = fy(uthours)
		hz = fz(uthours)
		
		nhr = uthours.size
		
		for i in range(0,nhr):
			hrlabel = '{:02d}'.format(np.int32(uthours[i] % 24.0))+':00'
			zord = np.float32((hz[i] > 0.0) | (np.sqrt((hx[i]-mcenter[0])**2 + (hy[i]-mcenter[1])**2) > 1.0))*2.0 - 1.0
			ax.scatter(hx[i],hy[i],color=[1.0,0.5,0.0],zorder=zord)
			if hx[i] >= xrnge[0] and hx[i] <= xrnge[1] and hy[i] >= yrnge[0] and hy[i] <= yrnge[1]:
				ax.text(hx[i],hy[i],hrlabel,color=[1.0,0.5,0.0],zorder=zord)
		
	if ShowDates:
			
		utcont = np.copy(data.ut)
		diffdate = np.where(data.Date[:-1] != data.Date[1:])[0]
		dates = []
		if diffdate.size > 0:
			for i in range(0,diffdate.size):
				dd = TT.DateDifference(data.Date[diffdate[i]],data.Date[diffdate[i]+1])
				dates.append(data.Date[diffdate[i]+1])
				utcont[diffdate[i]+1:] += 24.0*dd
			dateut = (np.arange(diffdate.size)+1)*24.0

			fx = InterpolatedUnivariateSpline(utcont,px)
			fy = InterpolatedUnivariateSpline(utcont,py)
			fz = InterpolatedUnivariateSpline(utcont,pz)
			
			dx = fx(dateut)
			dy = fy(dateut)
			dz = fz(dateut)		
			
			for i in range(0,diffdate.size):
				zord = np.float32((dz[i] > 0.0) | (np.sqrt((dx[i]-mcenter[0])**2 + (dy[i]-mcenter[1])**2) > 1.0))*2.0 - 1.0
				ax.scatter(dx[i],dy[i],color=[0.0,0.0,0.0],zorder=zord)
				if dx[i] >= xrnge[0] and dx[i] <= xrnge[1] and dy[i] >= yrnge[0] and dy[i] <= yrnge[1]:
					ax.text(dx[i],dy[i],'{:08d}'.format(dates[i]),color=[0.0,0.0,0.0],zorder=zord)
	
	if ShowMP:
		amp = np.pi*(np.arange(359)-179)/180
		Rmp = Rss*np.sqrt(2.0/(1.0+np.cos(amp)))
		aplot = np.linspace(-180,180,361)*np.pi/180.0
		MP = {	'XY':(Rmp*np.cos(amp),Rmp*np.sin(amp)),
				'YX':(Rmp*np.sin(amp),Rmp*np.cos(amp)),
				'YZ':(Rss*np.sqrt(2.0)*np.cos(aplot),Rss*np.sqrt(2.0)*np.sin(aplot)),
				'ZY':(Rss*np.sqrt(2.0)*np.cos(aplot),Rss*np.sqrt(2.0)*np.sin(aplot)),
				'XZ':(Rmp*np.cos(amp),Rmp*np.sin(amp)),
				'ZX':(Rmp*np.sin(amp),Rmp*np.cos(amp)),}
		mpx,mpy = MP[Plane]
		ax.plot(mpx,mpy,color=[0.0,0.0,1.0],linewidth=2.0)		
		
	return ax
