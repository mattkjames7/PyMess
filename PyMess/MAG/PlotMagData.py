from .ReadMagData import ReadMagData
from .ReadRotatedData import ReadRotatedData
from .MagDataMPN import MagDataMPN
from scipy.signal import detrend
import numpy as np
import matplotlib.pyplot as plt
import KT17 as kt17
from .. import Globals
import DateTimeTools as TT
import RecarrayTools as RT
from ..Tools.DTPlotLabel import DTPlotLabel
from scipy.interpolate import interp1d,InterpolatedUnivariateSpline
from ..Pos.GetAberrationAngle import GetAberrationAngle

def PlotMagData(Date,ut=[0,24.0],MagType='MSM',Ab=None,Minute=False,Bmag=True,Res=None,Detrend=False,LoFilt=None,HiFilt=None,fig=None,maps=[1,1,0,0],noxlabel=False,LegSize=None,ShowModel=False,ShowBS=True,ShowMP=True,ShadeCrossings=True,ShowEqCrossings=True,LegBG=True,LegLoc='upper right'):
	'''
	Plots magnetometer data.
	
	Inputs:
		Date: Single element integer or 2-elements integer date, or date 
			range, where dates are in the format yyyymmdd.
		ut: 2 element floating point list, array or tuple specifying the
			time range to plot within
		MagType: String specifying which magnetometer data to plot:
			'MSM' -  Plots MAG data in MSM coords (default)
			'Rotated' - Plots MAG data rotated into toroidal, poloidal
				and parallel components (useful for ULF waves)
			'MPN' - Plots MAG data in magnetopause normal coordinates
				of some decription. Not 100% sure if these are right.
		Ab: Aberration angle or magnetosphere - set to None to calculate
			automatically
		Minute: Boolean, True for minute data, False for full data.
		Bmag: Plot |B| when True.
		Res: Set to some desired time resolution in seconds to resample
			data (e.g. Res=0.05 for 20Hz sampling) - required for 
			low and high pass filtering.
		Detrend: Removes any linear trends from the data when True.
		LoFilt: Low pass filter, set to cutoff period in seconds.
		HiFilt: High pass filter, set to cutoff period in seconds.
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
		LegSize: set to real value to sontrol size of the legend.
		ShowModel: Shows the model magnetic field is set to True.
		ShowBS: Shows bow shock crossings.
		ShowMP: Show magnetopause crossings.
		ShadeCrossings: Shades magnetopause and bow shock crossings.
		ShowEqCrossings: Shows when MESSENGER crosses the magnetic 
			equatorial plane.
		LegBG: Boolean to control whether the background of the legend
			is visible or not.
		LegLoc: Constrols the location of the legend.
	
	'''

	#Get data function and labels
	if MagType == 'MPN':
		DataFunc = MagDataMPN
		PlotLabels = ['$B_N$','$B_M$','$B_L$']
		DataLabels = ['BN','BM','BL']
	elif MagType == 'Rotated':
		DataFunc = ReadRotatedData
		PlotLabels = ['$B_P$','$B_T$','$B_{||}$']
		DataLabels = ['Bpol','Btor','Bpar']
	else:
		DataFunc = ReadMagData
		PlotLabels = ['$B_x$','$B_y$','$B_z$']
		DataLabels = ['Bx','By','Bz']

	#MPData = Globals.W13MP
	#BSData = Globals.W13BS

	#list all of the dates to load
	if np.size(Date) == 1:
		dates = [Date]
	else:
		dates = []
		d = Date[0]
		while d <= Date[1]:
			dates.append(d)
			d = TT.PlusDay(d)
			
	#now to load all of those dates
	nd = np.size(dates)
	data = DataFunc(dates[0],Minute=Minute,res=res,Ab=Ab)
	if nd > 1:
		for i in range(1,nd):
			tmp = DataFunc(dates[i],Minute=Minute,res=res,Ab=Ab)
			data = RT.JoinRecarray(data,tmp)
			
	#now to remove anything that is out of the desired time range
	#and anything with random huge spikes in |B|
	Bm = np.sqrt(data[DataLabels[0]]**2 + data[DataLabels[1]]**2 + data[DataLabels[2]]**2)
	if nd == 1:
		use = np.where((data.ut >= ut[0]) & (data.ut <= ut[1]) & (Bm < 600.0))[0]
	else:
		use = np.where((((data.Date == dates[0]) & (data.ut >= ut[0])) |
						((data.Date == dates[-1]) & (data.ut <= ut[1])) |
						((data.Date > dates[0]) & (data.Date < dates[-1]))) &
						(Bm < 600))[0]
	data = data[use]
	Bm = Bm[use]
	
	#could do with a continuous time axis for plotting against
	#also going to extract other variables we need from the data object
	Date = data.Date
	UT = data.ut
	UTc = np.copy(UT)
	B0 = data[DataLabels[0]]
	B1 = data[DataLabels[1]]
	B2 = data[DataLabels[2]]
	Zmsm = data.Zmsm

	day = np.where(Date[1:] != Date[:-1])[0]
	for i in range(0,day.size):
		dd = TT.DateDifference(Date[day[i]],Date[day[i]+1])
		UTc[day[i]+1:] += dd*24.0

	#detrend data if needed
	if Detrend == True:
		good = np.where(np.isfinite(Bm))[0]
		B0[good] = detrend(B0[good])
		B1[good] = detrend(B1[good])
		B2[good] = detrend(B2[good])


	#low pass filter data - must be resamples though first!
	if not LoFilt is None and not res is None: #low-pass filter
		lob0 = TT.lsfilter(B0,res,LoFilt,res)
		lob1 = TT.lsfilter(B1,res,LoFilt,res)
		lob2 = TT.lsfilter(B2,res,LoFilt,res)	
		B0 = lob0
		B1 = lob1
		B2 = lob2
		
	#high pass filter data - must be resamples though first!
	if not HiFilt is None and not res is None: #high-pass filter
		lob0 = TT.lsfilter(B0,res,HiFilt,res)
		lob1 = TT.lsfilter(B1,res,HiFilt,res)
		lob2 = TTlsfilter(B2,res,HiFilt,res)	
		
		B0 = B0-lob1
		B1 = B1-lob2
		B2 = B2-lob3	

	#set plot limits on y-axis
	maxb=np.nanmax(bm)
	if maxb > 500.0:
		maxb = 500.0
	yrnge=[-maxb,maxb]
		
	#create plot
	if fig == None:
		fig=plt
		fig.figure()
	fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
	ax = fig.axis([UTc[0],UTc[-1],yrnge[0],yrnge[1]])
	
	colors = [[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]
	B = [B0,B1,B2]
	for i in range(0,3):
		ax.plot(UTc,B[i],color=colors[i],label=PlotLabels[i],linewidth=1.0)
	fig.plot([UTc[0],UTc[-1]],[0.0,0.0],color=[0.0,0.0,0.0],linestyle='-',linewidth=1.0)
	if Bmag == True:		
		fig.plot(UTc,Bm,color=[0.0,0.0,0.0],label='$\pm \mathbf{|B|}$',linewidth=1.0)
		fig.plot(UTc,-Bm,color=[0.0,0.0,0.0],linewidth=1.0)
	
	#show the model field if desired
	if ShowModel:
		#get MESSENGER position
		p0 = data.Xmsm
		p1 = data.Ymsm
		p2 = data.Zmsm
		
		#Get distance from the sun for all dates, plus surrounding dates
		mdates = np.copy(dates)
		mdates = np.append(TT.MinusDay(dates[0]),mdates)
		mdates = np.append(mdates,TT.PlusDay(dates[-1]))
		mut = np.arange(mdates.size)*24.0 - 12 # each Rsun is as midday
		
		mRsun = np.zeros(mdates.size,dtype='float32')
		for i in range(0,mdates.size):
			mRsun[i] = (GetAberrationAngle(mdates[i])).Angle
	
		#interpolate 
		fRsun = InterpolatedUnivariateSpline(mut,mRsun)
		Rsun = fRsun(Utc)
		
		#get parameter array
		Params = np.array([Rsun,[50.0]*Rsun.size]).T
	
		m0,m1,m2 = kt17.ModelField(p0,p1,p2,Params=Params)
		fig.plot(UTc,m0,color=[1.0,0.0,0.0],linestyle='--')
		fig.plot(UTc,m1,color=[0.0,1.0,0.0],linestyle='--')
		fig.plot(UTc,m2,color=[0.0,0.0,1.0],linestyle='--')		

	# if ShowMP:
		# MPCut = MPData.ut[useMP]
		# MPCDate = MPData.date[useMP]
		# MPT = MPData.ctype[useMP]
	# else:
		# MPCut = np.array([])
		# MPDate = np.array([])
			
	# if ShowBS:
		# BSCut = BSData.ut[useBS]
		# BSCDate = BSData.date[useBS]
		# BST = BSData.ctype[useBS]
	# else:
		# BSCut = np.array([])
		# BSDate = np.array([])
		
	# for i in range(1,MPCut.size):
		# if MPCut[i] < MPCut[i-1]:
			# MPCut[i:]+=24.0	
	# for i in range(1,BSCut.size):
		# if BSCut[i] < BSCut[i-1]:
			# BSCut[i:]+=24.0	
			
	# if MPCut.size > 0:
		# for t in MPCut:
			# if t == MPCut[0]:
				# labelm = 'MP Crossing' 
			# else:
				# labelm = None
			# fig.plot([t,t],[yrnge[0],yrnge[1]],color='orange',label=labelm)
		# if ShadeCrossings:
			# for i in range(1,MPCut.size):
				# if ((MPT[i-1] == 3) and (MPT[i] == 4)) or ((MPT[i-1] == 5) and (MPT[i] == 6)):
					# fig.fill([MPCut[i-1],MPCut[i],MPCut[i],MPCut[i-1]],[yrnge[0],yrnge[0],yrnge[1],yrnge[1]],color=[1.0,0.5,0.0,0.25])
	# if BSCut.size > 0:
		# for t in BSCut:
			# if t == BSCut[0]:
				# labelb = 'BS Crossing' 
			# else:
				# labelb = None
			# fig.plot([t,t],[yrnge[0],yrnge[1]],color='red',label=labelb)
		# if ShadeCrossings:
			# for i in range(1,BSCut.size):
				# if ((BST[i-1] == 1) and (BST[i] == 2)) or ((BST[i-1] == 7) and (BST[i] == 8)):
					# fig.fill([BSCut[i-1],BSCut[i],BSCut[i],BSCut[i-1]],[yrnge[0],yrnge[0],yrnge[1],yrnge[1]],color=[1.0,0.0,0.0,0.25])
	
	if ShowEqCrossings:
		eq = np.where(((Zmsm[1:] > 0) & (Zmsm[:-1] <= 0)) | ((Zmsm[1:] < 0) & (Zmsm[:-1] >= 0)))[0]
		if eq.size > 0:
			R = fig.axis()
			eqt = np.zeros(eq.size,dtype='float32')
			for i in range(0,eq.size):
				f = interp1d([Zmsm[eq[i]],Zmsm[eq[i]+1]],[UTc[eq[i]],UTc[eq[i]+1]])
				eqt[i] = f(0.0)
			fig.vlines(eqt,R[2],R[3],color=[0.0,0.0,0.0],linestyle='--',label='Magnetic Equator')		
	
	ax=fig.gca()
	
	if noxlabel == False:
		DTPlotLabel(ax,UTc,Date,Seconds=False,IncludeYear=False)
		fig.xlabel('UT')
	else:
		ax.xaxis.set_visible(False)
		

	fig.ylabel('B Field [nT]')
	
	if LegLoc[:3] == 'out':
		ll = LegLoc.split()[1]
		
		if ll == 'right':
			LegLoc = 'center left'
			bbox_to_anchor = (1.0,0.5)
		elif ll == 'left':
			LegLoc = 'center right'
			bbox_to_anchor = (0.0,0.5)
		elif ll == 'top':
			LegLoc = 'lower center'
			bbox_to_anchor = (0.5,1.0)
		elif ll == 'bottom':
			LegLoc = 'upper center'
			bbox_to_anchor = (0.5,0.0)
	else:
		bbox_to_anchor = None		
	
	if LegSize == None:
		legend = ax.legend(loc=LegLoc,bbox_to_anchor=bbox_to_anchor)	
	else:
		legend = ax.legend(loc=LegLoc,bbox_to_anchor=bbox_to_anchor,prop={'size':LegSize})	
	if LegBG:
		legend.get_frame().set_facecolor([1.0,1.0,1.0,1.0])
		legend.get_frame().set_edgecolor([0.0,0.0,0.0,1.0])
	return fig


