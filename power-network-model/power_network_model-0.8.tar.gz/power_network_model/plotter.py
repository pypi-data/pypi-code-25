"""
Contains the function network_plotter() to plot the power network model using Basemap
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def network_plotter(trafo_file, connections_file, input_colors, image_title):
    """ Make a pretty(ish) plot of the network using Basemap.

            Parameters
            -----------
            trafo_file = location of output transformers file
            connections_file = location of output connections file
            input_colors = list of colors for voltages in network: i.e., ["black", "red"] for a 2-voltage network
            image_title = title for the output image of this function

            Returns
            -----------
            pretty plot to be saved at your leasure
            -----------------------------------------------------------------

    """
    # Read in the transformer info first
    a, b, c, d, e, f, z = np.loadtxt(trafo_file, usecols = (0, 1, 2, 3, 4, 5, 8), unpack = True)

    sitenum = a
    geolat = b
    geolon = c
    voltages = f

    voltages_for_colors = sorted(list(set(voltages)), reverse = True)

    colors = [input_colors[voltages_for_colors.index(x)] for x in voltages]

    #-------------------------------------------------------------------------------
    # Read in connections info
    a2, b2, c2, d2, e2, f2, z2 = np.loadtxt(connections_file, usecols = (0, 1, 2, 3, 4, 5, 8), unpack = True)

    latsfrom = [geolat[list(sitenum).index(x)] for x in a2]
    lonsfrom = [geolon[list(sitenum).index(x)] for x in a2]

    latsto = [geolat[list(sitenum).index(x)] for x in b2]
    lonsto = [geolon[list(sitenum).index(x)] for x in b2]

    lineresist = c2

    connections = np.ones(len(latsfrom))

    t_cnn = sorted(list(set(list(a2) + list(b2))))

    colors2 = []
    for i in z2:
        if np.isnan(i):
            colors2.append("black")
        else:
            colors2.append(input_colors[voltages_for_colors.index(i)])
    ################################################################################
    # Plot 1 - Initial Selection

    plt.clf()

    fig = plt.figure(1)
    ax = plt.subplot(111)

    water = "CadetBlue"
    land = "AliceBlue"

    ww = 'white'
    bb = 'black'

    maxlat, minlat = max(geolat), min(geolat)
    diflat = maxlat - minlat

    maxlon, minlon = max(geolon), min(geolon)
    diflon = maxlon - minlon

    m = Basemap(projection = 'merc', llcrnrlat= minlat - diflat/10., urcrnrlat= maxlat + diflat/10., llcrnrlon=minlon - diflon/10., urcrnrlon= maxlon + diflon/10, resolution='l',area_thresh=100)

    m.drawcoastlines(color = 'k', linewidth = 2)
    m.drawparallels(np.arange(0,360,0.5) ,labels=[1, 0, 0, 0], color = 'k', fontsize =24)
    m.drawmeridians(np.arange(0,360,1),labels=[0,0,0,1], color = 'k', fontsize =24)
    m.drawcountries(linewidth = 2)
    m.drawmapboundary(fill_color=water)
    m.fillcontinents(color=land,lake_color=water)

    xxx, yyy = m(geolon, geolat)
    coll = ax.scatter(xxx, yyy, color=colors, picker = 2, s=200, zorder = 100)

    ref_points = []

    for index, value in enumerate(a2):
        
        a = [lonsfrom[index], lonsto[index]]
        b = [latsfrom[index], latsto[index]]
        xxx, yyy = m(a, b)

        plt.plot(xxx, yyy, c = colors2[index], linestyle = "-", zorder = 100)

        ref_points.append(xxx + yyy)
        
        fig.canvas.draw()


    plt.title(image_title, fontsize = 24)

    plt.show()

################################################################################
################################################################################

