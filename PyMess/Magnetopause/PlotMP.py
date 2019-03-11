import numpy as np

def PlotMPxy(fig,Rss=1.42,Alpha=0.5,color=[0.0,0.0,1.0],linewidth=2.0,linestyle='-'):
	
	theta = (np.arange(359,dtype='float32')-179.0)*np.pi/180.0
	R = Rss*(2.0/(1.0 + np.cos(theta)))**Alpha
	x = R*np.cos(theta)
	y = R*np.sin(theta)
	
	fig.plot(x,y,color=color,linestyle=linestyle,linewidth=linewidth)
	
def PlotMPyx(fig,Rss=1.42,Alpha=0.5,color=[0.0,0.0,1.0],linewidth=2.0,linestyle='-'):
	
	theta = (np.arange(359,dtype='float32')-179.0)*np.pi/180.0
	R = Rss*(2.0/(1.0 + np.cos(theta)))**Alpha
	x = R*np.cos(theta)
	y = R*np.sin(theta)
	
	fig.plot(y,x,color=color,linestyle=linestyle,linewidth=linewidth)
