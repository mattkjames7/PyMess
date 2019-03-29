import numpy as np
from .ReadFIPS import ReadFIPS
import DateTimeTools as TT


def GetFIPS(Date,ut,Type='60'):
	'''
	Retrieves FIPS data from a specific time range
	
	'''
