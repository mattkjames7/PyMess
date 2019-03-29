import numpy as np
import matplotlib.pyplot as plt
from .ReadFIPS import ReadFIPS
import DateTimeTools as TT


Parameters = {	'n':	('Density (cm$^{-3}$)','n',[1.0,0.5,0.0]),
				'T':	('Temperature (MK)','t',[0.0,0.5,1.0]),
				'p':	('Pressure (nPA)','p',[0.5,0.5,1.0]),
				'nk':	('$\kappa$ - Density (cm$^{-3}$)','nk',[1.0,0.5,0.0]),
				'Tk':	('$\kappa$ - Temperature (MK)','tk',[0.0,0.5,1.0]),
				'pk':	('$\kappa$ - Pressure (nPA)','pk',[0.5,0.5,1.0]),
				'K':	('$\kappa$','k',[1.0,0.5,0.5]),}

def PlotFIPS(Date,ut,Param='nk',fig=None,maps=[1,1,0,0],ylog=False,no_x=False,MaxGap=120.0,**kwargs):
	'''
	A simple procedure to plot a time series of plasma parameters.
	
	'''

	defaults = {'ms':1.0}
	kwargs.update(defaults)
	
	data = 
