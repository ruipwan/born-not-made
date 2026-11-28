"""Bilinearly sample a computed height field on the larger optical display mesh."""
import numpy as np

class SampledSurface:
    def __init__(self, path):
        with np.load(path) as sample:
            self.frames = sample['frames']
            grid_x, grid_y = sample['x'], sample['y']
        self.x = np.linspace(-.67,.67,181)
        self.y = np.linspace(-.38,.38,101)
        self.ix,self.fx = self.weights(grid_x,self.x)
        self.iy,self.fy = self.weights(grid_y,self.y)

    @staticmethod
    def weights(source, target):
        p=np.clip((target-source[0])/(source[1]-source[0]),0,len(source)-1)
        i=np.minimum(p.astype(int),len(source)-2)
        return i, p-i

    def displacement(self, t):
        frame=self.frames[round(24*t)]
        horizontal=frame[:,self.ix]*(1-self.fx)+frame[:,self.ix+1]*self.fx
        return horizontal[self.iy,:]*(1-self.fy[:,None])+horizontal[self.iy+1,:]*self.fy[:,None]
