import os
import numpy as np
import pandas as pd
from scipy import io
%pylab
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import geopandas as gpd

homedir = os.path.expanduser('~')

ua = gpd.read_file(homedir + '/GIS/cb_2014_us_ua10_500k.shp')
aa_geom = ua[ua['NAME10'].str.contains('Ann Arbor')].geometry.explode().reset_index().geometry
aa_bounds = np.asarray(ua[ua['NAME10'].str.contains('Ann Arbor')].geometry.total_bounds)[[0,2,1,3]]

v = io.loadmat(homedir + '/Desktop/final.mat')
v = pd.DataFrame(v['H'], columns=['lat', 'lon', 'wiper', 'id', 'time'])

v['time'] = pd.to_datetime(v['time'].astype(int).astype(str).str.pad(12, fillchar='0'), format="%y%m%d%H%M%S")

# ID counts per day

vc = v.set_index('time')['id'].resample('d', how='unique').str.len()
#vc.str.len().idxmax()

# Storm day

storm = v.set_index('time').loc['20090625']
storm = storm.resample('s').interpolate()

#storm['c'] = storm.wiper.map({0: 'blue', 1:'green', 2:'yellow', 3:'red', 4:'purple'})
#storm = storm.resample('10s')

#fig = plt.figure()

# Scatterplot streamer CUSTOM

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class AnimatedScatter(object):
    """An animated scatter plot using matplotlib.animations.FuncAnimation."""
    def __init__(self, data_src, xlabels, ylabels):
        self.xlabels = xlabels
	self.ylabels = ylabels
	self.xbounds = aa_bounds[[0,1]]
	self.ybounds = aa_bounds[[2,3]]
        self.stream = self.data_stream(data_src)

        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=1, 
                                           init_func=self.setup_plot, blit=True)

    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        x, y = next(self.stream)
	# self.backdrop = self.ax.plot([self.xbounds[0], self.xbounds[1]], [self.ybounds[0], self.ybounds[1]])
        for i in aa_geom.index:
            self.ax.plot(aa_geom.iloc[i].exterior.xy[0],
			    aa_geom.iloc[i].exterior.xy[1], color='green')
        self.scat = self.ax.scatter(x, y, animated=True)
        self.ax.axis([self.xbounds[0], self.xbounds[1],
		      self.ybounds[0], self.ybounds[1]])

        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def data_stream(self, data_src):
        """Generate a random walk (brownian motion). Data is scaled to produce
        a soft "flickering" effect."""

	data = data_src

        for i in data.index.unique():
            xy = data.loc[i, [self.xlabels, self.ylabels]].values
            # s += 0.05 * (np.random.random(self.numpoints) - 0.5)
            # c += 0.02 * (np.random.random(self.numpoints) - 0.5)
            yield xy

    def update(self, i):
        """Update the scatter plot."""
        data = next(self.stream)

        # Set x and y data...
        self.scat.set_offsets(data)
        # Set sizes...
        # self.scat._sizes = 300 * abs(data[2])**1.5 + 100
        # Set colors..
        # self.scat.set_array(data[3])

        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def show(self):
        plt.show()

# Scatterplot animator 1

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class AnimatedScatter(object):
    """An animated scatter plot using matplotlib.animations.FuncAnimation."""
    def __init__(self, numpoints=50):
        self.numpoints = numpoints
        self.stream = self.data_stream()

        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=5, 
                                           init_func=self.setup_plot, blit=True)

    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        x, y, s, c = next(self.stream)
        self.scat = self.ax.scatter(x, y, c=c, s=s, animated=True)
        self.ax.axis([-10, 10, -10, 10])

        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def data_stream(self):
        """Generate a random walk (brownian motion). Data is scaled to produce
        a soft "flickering" effect."""
        data = np.random.random((4, self.numpoints))
        xy = data[:2, :]
        s, c = data[2:, :]
        xy -= 0.5
        xy *= 10
        while True:
            xy += 0.03 * (np.random.random((2, self.numpoints)) - 0.5)
            s += 0.05 * (np.random.random(self.numpoints) - 0.5)
            c += 0.02 * (np.random.random(self.numpoints) - 0.5)
            yield data

    def update(self, i):
        """Update the scatter plot."""
        data = next(self.stream)

        # Set x and y data...
        self.scat.set_offsets(data[:2, :])
        # Set sizes...
        self.scat._sizes = 300 * abs(data[2])**1.5 + 100
        # Set colors..
        self.scat.set_array(data[3])

        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def show(self):
        plt.show()

# Scatterplot animator 2

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

def main():
    numframes = 100
    numpoints = 10
    color_data = np.random.random((numframes, numpoints))
    x, y, c = np.random.random((3, numpoints))

    fig = plt.figure()
    scat = plt.scatter(x, y, c=c, s=100)

    ani = animation.FuncAnimation(fig, update_plot, frames=xrange(numframes),
                                  fargs=(color_data, scat))

def update_plot(i, data, scat):
    scat.set_array(data[i])
    return scat,

main()
