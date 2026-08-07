"""Plot time series of combined MESSENGER FIPS plasma parameters."""

import matplotlib.pyplot as plt
import numpy as np
import DateTimeTools as TT

from .GetData import GetData
from ..Tools.InsertGaps import InsertGaps


Parameters = {
	'n': ('Density (cm$^{-3}$)', 'n', [1.0, 0.5, 0.0]),
	'T': ('Temperature (MK)', 't', [0.0, 0.5, 1.0]),
	'p': ('Pressure (nPa)', 'p', [0.5, 0.5, 1.0]),
	'nk': (r'$\kappa$ density (cm$^{-3}$)', 'nk', [1.0, 0.5, 0.0]),
	'Tk': (r'$\kappa$ temperature (MK)', 'tk', [0.0, 0.5, 1.0]),
	'pk': (r'$\kappa$ pressure (nPa)', 'pk', [0.5, 0.5, 1.0]),
	'K': (r'$\kappa$', 'k', [1.0, 0.5, 0.5]),
}

_ParameterAliases = {
	't': 'T',
	'tk': 'Tk',
	'k': 'K',
}


def _Axes(fig, maps):
	"""Create or select an axes while retaining the package's maps API."""
	if hasattr(fig, 'plot') and hasattr(fig, 'xaxis'):
		return fig
	if fig is None:
		figure = plt.figure()
	elif hasattr(fig, 'gcf'):
		figure = fig.gcf()
	else:
		figure = fig

	if len(maps) != 4:
		raise ValueError('maps must contain [columns, rows, column, row]')
	columns,rows,column,row = [int(value) for value in maps]
	if columns < 1 or rows < 1 or not 0 <= column < columns or not 0 <= row < rows:
		raise ValueError('maps specifies an invalid subplot position')
	index = row*columns + column + 1
	return figure.add_subplot(rows,columns,index)


def PlotFIPS(Date,ut,Param='nk',fig=None,maps=(1,1,0,0),ylog=False,
			 no_x=False,MaxGap=120.0,Type='60H',**kwargs):
	"""Plot one combined FIPS plasma parameter over a requested time range.

	Parameters
	----------
	Date : int or array-like
		A date, explicit dates, or a two-date range in ``yyyymmdd`` format.
	ut : two-element array-like
		UT range in hours. For a date range this applies to the first and last
		dates respectively.
	Param : str
		One of ``n``, ``T``, ``p``, ``nk``, ``Tk``, ``pk`` or ``K``.
	fig : matplotlib Figure, Axes, or pyplot module, optional
		Plot target. A new figure is created when omitted.
	maps : sequence
		Legacy subplot location ``[columns, rows, column, row]``.
	ylog : bool
		Use a logarithmic parameter axis.
	no_x : bool
		Hide the time-axis label and tick labels.
	MaxGap : float or None
		Break connecting lines across gaps larger than this many seconds.
	Type : str
		Combined-data type passed to :func:`GetData`; defaults to ``60H``.
	**kwargs
		Additional keyword arguments passed to ``Axes.plot``.

	Returns
	-------
	matplotlib.axes.Axes
	"""
	Param = _ParameterAliases.get(Param,Param)
	if Param not in Parameters:
		raise ValueError(
			'Unknown FIPS parameter {!r}; choose from {}'.format(
				Param,', '.join(Parameters)
			)
		)

	data = GetData(Date,ut=ut,Type=Type,Verbose=False)
	if data.size == 0:
		raise ValueError('No {:s} FIPS data found in the requested interval'.format(Type))

	label,field,color = Parameters[Param]
	time = np.asarray(data.unix,dtype='float64')
	values = np.asarray(data[field],dtype='float64')
	order = np.argsort(time)
	time = time[order]
	values = values[order]
	if MaxGap is not None:
		time,values = InsertGaps(
			time,values,MaxGap=MaxGap,SecondsPerUnit=1.0
		)

	ax = _Axes(fig,maps)
	if 'ms' not in kwargs and 'markersize' not in kwargs:
		kwargs['markersize'] = 1.0
	kwargs.setdefault('marker','.')
	kwargs.setdefault('linestyle','-')
	kwargs.setdefault('color',color)
	ax.plot(time,values,**kwargs)
	ax.set_ylabel(label)
	if ylog:
		ax.set_yscale('log')

	if no_x:
		ax.tick_params(axis='x',which='both',bottom=False,labelbottom=False)
		ax.set_xlabel('')
	else:
		TT.DTPlotLabel(ax,Seconds=False,IncludeYear=False,TimeFMT='unix')
		ax.set_xlabel('UT')
	return ax
