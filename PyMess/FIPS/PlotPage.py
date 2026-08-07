"""Create a standard summary page for combined MESSENGER FIPS data."""

import matplotlib.pyplot as plt
import DateTimeTools as TT

from .GetData import GetData
from .PlotFIPS import PlotFIPS
from .PlotFIPSSpectrogram import PlotFIPSSpectrogram


_CombinedTypes = ('60H','60He','60He2','60Na','60O','10H')


def PlotPage(Date,ut=(0.0,24.0),Type='60H',Y='Energy',cmap='gnuplot',
			 MaxGap=120.0,MomentLog=True):
	"""Plot an A4 portrait summary of one combined FIPS product.

	Parameters
	==========
	Date : int or two-element array
		A single yyyymmdd date or an inclusive date range.
	ut : two-element array
		UT range in hours. For multiple dates, the values limit the first
		and last dates respectively.
	Type : str
		Combined product: ``60H``, ``60He``, ``60He2``, ``60Na``, ``60O``
		or ``10H``.
	Y : str
		Spectrogram vertical coordinate: ``Energy`` or ``Velocity``.
	cmap : str or Colormap
		Spectrogram colour map.
	MaxGap : float or None
		Break plots across gaps larger than this many seconds.
	MomentLog : bool
		Use logarithmic axes for density, temperature and pressure.

	Returns
	=======
	figure, axes
		The Matplotlib figure and its six axes.
	"""
	if Type not in _CombinedTypes:
		raise ValueError(
			'Type must be a combined FIPS product: {:s}'.format(
				', '.join(_CombinedTypes)
			)
		)

	data = GetData(Date,ut=ut,Type=Type,Verbose=False)
	if data.size == 0:
		raise ValueError('No {:s} FIPS data found in the requested interval'.format(Type))

	figure,axes = plt.subplots(
		6,1,figsize=(8.27,11.69),sharex=True,constrained_layout=True,
		gridspec_kw={'height_ratios':(1.25,1.25,1.25,0.8,0.8,0.8)},
	)

	for ax,param in zip(axes[:3],('Counts','Flux','PSD')):
		PlotFIPSSpectrogram(
			Date,ut,Param=param,Y=Y,fig=ax,no_x=True,MaxGap=MaxGap,
			Type=Type,cmap=cmap,data=data,
		)
		ax.set_title(param,loc='left',fontsize='medium')

	moments = (
		('n','nk','Density (cm$^{-3}$)'),
		('T','Tk','Temperature (MK)'),
		('p','pk','Pressure (nPa)'),
	)
	for ax,(mb_param,kappa_param,ylabel) in zip(axes[3:],moments):
		PlotFIPS(
			Date,ut,Param=mb_param,fig=ax,ylog=MomentLog,no_x=True,
			MaxGap=MaxGap,Type=Type,data=data,label='Maxwell-Boltzmann',
			color='tab:blue',
		)
		PlotFIPS(
			Date,ut,Param=kappa_param,fig=ax,ylog=MomentLog,no_x=True,
			MaxGap=MaxGap,Type=Type,data=data,label=r'$\kappa$',
			color='tab:orange',
		)
		ax.set_ylabel(ylabel)
		ax.legend(loc='best',fontsize='small')
		ax.grid(True,which='both',axis='y',alpha=0.2)

	axes[-1].tick_params(axis='x',which='both',bottom=True,labelbottom=True)
	TT.DTPlotLabel(
		axes[-1],Seconds=False,IncludeYear=True,TimeFMT='unix'
	)
	axes[-1].set_xlabel('UT')
	figure.suptitle('MESSENGER FIPS {:s}'.format(Type))
	return figure,axes
