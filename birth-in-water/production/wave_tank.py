"""Finite-depth linear water surface in a rectangular tank with reflecting walls.
Lengths in metres. Heights are a synthetic optical experiment. The shell is a
visual occluder and does not scatter this field. No propulsion is simulated.
"""
import numpy as np
class WaveTank:
 def __init__(self,nx=181,ny=101):
  self.lx,self.ly,self.depth=1.34,.76,.275
  self.x=np.linspace(-self.lx/2,self.lx/2,nx)
  self.y=np.linspace(-self.ly/2,self.ly/2,ny)
  kx=np.arange(61)*np.pi/self.lx
  ky=np.arange(39)*np.pi/self.ly
  self.cx=np.cos((self.x[:,None]+self.lx/2)*kx)
  self.cy=np.cos((self.y[:,None]+self.ly/2)*ky)
  k=np.hypot(ky[:,None],kx[None,:])
  # Dispersion relation for an inviscid, incompressible fluid of finite depth.
  self.omega=np.sqrt((9.81*k+.072/998*k**3)*np.tanh(k*self.depth))
  # Cosine coefficients of a shallow localized displacement near the mouth.
  # Remove mean height so the trial adds no net water to the tank.
  w=.041
  self.amp=(np.cos(ky[:,None]*(.38-.03))*np.cos(kx[None,:]*(.67+.36))
            *np.exp(-.5*(w*k)**2))
  self.amp[1:]*=2;self.amp[:,1:]*=2;self.amp[0,0]=0
  self.amp*=.0042/np.max(self.cy@self.amp@self.cx.T)
  # Bulk viscous damping plus an empirical basin loss, specified rather than fitted.
  self.loss=.23+2*1.0e-6*k*k
 def displacement(self,t):
  return self.cy@(self.amp*np.cos(self.omega*t)*np.exp(-self.loss*t))@self.cx.T
