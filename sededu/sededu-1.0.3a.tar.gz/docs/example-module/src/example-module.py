# This is a module to demonstrate how a model could be implemented in SedEdu
# The module is written and executed in Python


# IMPORT LIBLARIES
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widget
import utils


# SET PARAMETERS
pi = np.pi
t = np.linspace(-3*pi, 6*pi, 1000)

ampInit = 1
amp = ampInit
ampMax = 5
ampMin = 0

perInit = 2 #2*pi
per = perInit
perMax = 10
perMin = 0.1


# DEFINE FUNCTIONS
def update(event):

    # read values from the sliders/statics
    theamp = slide_amp.val # using "the" keeps main namespace clean
    theper = slide_per.val

    # compute new y values
    they = theamp * np.sin( ((2*pi)/(theper*pi)) * t )

    # update the plot
    sin_line.set_ydata(they)

    # replace in main namespace
    amp = theamp
    per = theper
    y = they

    # redraw the canvas
    fig.canvas.draw_idle()


def reset(event):

    # reset button
    slide_amp.reset()
    slide_per.reset()
    update(event)


# run the model once with the initial values
y = amp * np.sin( ((2*pi)/(per*pi)) * t )


# setup the figure
plt.rcParams['toolbar'] = 'None' # turn off the matplotlib toolbar in the figure
plt.rcParams['figure.figsize'] = 11, 7 # size of the figure in inches
fig, ax = plt.subplots() # gives us a figure object and axes object to manipulate and plot things into
fig.canvas.set_window_title('SedEdu -- example module') # title of the figure window
plt.subplots_adjust(left=0.075, bottom=0.1, top=0.95, right=0.5) # where do we want the limits of the axes object
ax.set_xlabel("t") # the axis xlabel
ax.set_ylabel("y") # the axis ylabel
plt.xlim(min(t), max(t)) # the axis x limits
plt.ylim(-ampMax*1.25, ampMax*1.25) # the axis y limits
ax.xaxis.set_major_locator(plt.MultipleLocator(base=pi)) # locate tick marks every pi
ax.xaxis.set_major_formatter( plt.FuncFormatter(lambda v, x: str(int(v/pi)) + '$\pi$') ) # label them with X$\pi$


# add plot elements
x_line = plt.plot([min(t), max(t)], [0, 0], ls=':', lw=1, color='gray')
y_line = plt.plot([0, 0], [-ampMax*1.5, ampMax*1.5], ls=':', lw=1, color='gray')
sin_line, = plt.plot(t, y, lw=1.5, color='blue')


# add slider
widget_color = 'lightgoldenrodyellow'

ax_amp = plt.axes([0.55, 0.85, 0.4, 0.05], facecolor=widget_color)
slide_amp = utils.MinMaxSlider(ax_amp, 'amplitude', ampMin, ampMax, 
    valinit=ampInit, valstep=0.1, valfmt='%g', transform=ax.transAxes)

ax_per = plt.axes([0.55, 0.725, 0.4, 0.05], facecolor=widget_color)
slide_per = utils.MinMaxSlider(ax_per, 'period', perMin, perMax, 
    valinit=perInit, valstep=0.1, valfmt='%g'+'$\pi$', transform=ax.transAxes)

btn_reset_ax = plt.axes([0.825, 0.5, 0.1, 0.04])
btn_reset = widget.Button(btn_reset_ax, 'Reset', color=widget_color, hovercolor='0.975')


# connect widgets
slide_amp.on_changed(update)
slide_per.on_changed(update)
btn_reset.on_clicked(reset)


# show the results
plt.show()
