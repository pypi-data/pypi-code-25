# interactive stratigraphic filter toy model


# IMPORT LIBLARIES
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widget
import utils

# SET PARAMETERS
time = 50
T = time
timestep = 1
dt = timestep
t = np.array(np.linspace(0, T, T+1/dt))

muInit = 0
mu = muInit
muMax = 1
muMin = -muMax

sigmaInit = 1
sigma = sigmaInit
sigmaMax = 2
sigmaMin = 0

yView = 50


# DEFINE FUNCTIONS
def generate_elevation(themu, thesigma):
    '''
    make the elevation record, start of the model run

    requires a mean and std dev for normal distribution to work
    '''
    nt = len(t)
    elev = np.zeros(nt)
    elev[0] = 0
    for j in np.arange(1,nt):
        jt = t[j]
        jump = np.random.normal(themu, thesigma, 1)
        elev[j] = elev[j-1] + jump

    return elev


def generate_stratigraphy(elev):
    '''
    make the final stratigraphy by applying the stratigraphic filter

    loop from end to beginning of time to check if elevation was ever lower
    '''
    nt = len(t)
    strat = np.zeros(nt)
    strat[-1] = elev[-1]
    for j in np.flipud(np.arange(0, nt-1)):
        strat[j] = np.array([elev[j], strat[j+1]]).min()

    return strat


def compute_bedthickness(strat):
    '''
    compute the thicknesses of beds preserved in the stratigraphy
    '''
    diff = strat[1:] - strat[:-1]
    thicks = diff[np.nonzero(diff)]
    if len(thicks) > 0:
        meanthick = np.mean(np.array(thicks))
    else:
        meanthick = 0

    return meanthick


def compute_statistics(elev, strat):
    '''
    function to compute statistics of the model run

    add more stats by appending to end of list and adding to table setup
    this really needs to be rewritten to use a dictionary
    '''
    stats = []
    stats.append( elev[-1] )                            # final elevation
    stats.append( (sum( elev == strat )-1) / T )        # fraction of time preserved
    stats.append( compute_bedthickness(strat) )         # thickness of beds preserved
    return stats


def run_model(event):
    '''
    the core model run method
        - can be triggered by multiple events or event wrappers
    '''
    # read values from the sliders/statics
    themu = slide_mu.val
    thesigma = slide_sigma.val
    T = time
    dt = timestep

    # compute one run
    t = np.linspace(0, T, T+1/dt)
    elev = generate_elevation(themu, thesigma)
    strat = generate_stratigraphy(elev)
    stats = compute_statistics(elev, strat)
    summ_stats = np.tile(np.nan, (len(stats), 1))
    print(summ_stats)

    # if summary stats is checked, compute more runs
    if chk_conn.get_status()[0]:
        nRun = 100
        summ_stats = stats
        for i in np.arange(1, nRun+1):
            ielev = generate_elevation(themu, thesigma)
            istrat = generate_stratigraphy(ielev)
            istats = compute_statistics(ielev, istrat) 
            print(istats[-1])       
            summ_stats = (summ_stats*(i-1) + istats) / i

    # update the plot and the table
    zero_line.set_ydata(np.zeros(len(t)))
    elev_line.set_data(t, elev)
    strat_line.set_data(t, strat)
    for tab_row in np.arange(1, np.size(tabData,0)+1):
        statsTable._cells[(tab_row, 0)]._text.set_text(utils.format_table_number(stats[tab_row-1]))
        statsTable._cells[(tab_row, 1)]._text.set_text(utils.format_table_number(summ_stats[tab_row-1]))

    # redraw the canvas
    fig.canvas.draw_idle()


def slider_wrapper(event):
    # this is a wrapper for the sliders to only run model if connected
    if chk_conn.get_status()[1]:
        run_model(event)


def reset(event):
    # reset button
    needs_run = False
    if any((slide_mu.val != slide_mu.valinit, 
            slide_sigma.val != slide_sigma.valinit)):
        needs_run = True
    slide_mu.reset()
    slide_sigma.reset()
    for cb in [i for i, x in enumerate(chk_conn.get_status()) if x]:
        chk_conn.set_active(cb)
    if needs_run:
        run_model(event)

    fig.canvas.draw_idle()


# run the program once with the initial values
elev = generate_elevation(muInit, sigmaInit)
strat = generate_stratigraphy(elev)
stats = compute_statistics(elev, strat)
summ_stats = np.tile(np.nan, (len(stats), 1)) # fill nans for init


# setup the figure
plt.rcParams['toolbar'] = 'None'
plt.rcParams['figure.figsize'] = 11, 7
fig, ax = plt.subplots()
fig.canvas.set_window_title('SedEdu -- stratigraphic filter toy')
plt.subplots_adjust(left=0.075, bottom=0.1, top=0.95, right=0.5)
background_color = 'white'
ax.set_xlabel("time")
ax.set_ylabel("elevation")
plt.ylim(-yView, yView)


# add plot elements
zero_line, = plt.step(t, np.zeros(len(t)), linestyle=":", lw=1.5, color='black')
strat_line, = plt.step(t, strat, lw=2, color='red')
elev_line, = plt.step(t, elev, lw=1.5, color='grey')


# add slider
widget_color = 'lightgoldenrodyellow'

ax_mu = plt.axes([0.55, 0.85, 0.4, 0.05], facecolor=widget_color)
slide_mu = utils.MinMaxSlider(ax_mu, 'mean of elevation change', muMin, muMax, 
    valinit=muInit, valstep=0.05, valfmt='%g', transform=ax.transAxes)

ax_sigma = plt.axes([0.55, 0.725, 0.4, 0.05], facecolor=widget_color)
slide_sigma = utils.MinMaxSlider(ax_sigma, 'std. dev. of change', sigmaMin, sigmaMax, 
    valinit=sigmaInit, valstep=0.1, transform=ax.transAxes)


# add table
statsNames = ['Final elevation', 'Frac. time preserved', 'mean bed thickness']
columnNames = ['this run', 'of 100 runs']
ax_statsTable = plt.axes([0.6, 0.325, 0.5, 0.1], frameon=False, xticks=[], yticks=[])
tabData = np.tile(['0', '0'], (len(statsNames), 1))
statsTable = plt.table(cellText=tabData, rowLabels=statsNames,
                       colLabels=columnNames, colWidths=[0.2, 0.2],
                       loc="center")
statsTable.scale(1, 1.5) # xscale, yscale of cells
for tab_row in np.arange(1, np.size(tabData,0)+1):
    statsTable._cells[(tab_row, 0)]._text.set_text(utils.format_table_number(stats[tab_row-1]))
    statsTable._cells[(tab_row, 1)]._text.set_text(utils.format_table_number(summ_stats[tab_row-1]))


# add gui buttons
chk_conn_ax = plt.axes([0.55, 0.5, 0.25, 0.15], facecolor=background_color)
chk_conn_list = ['compute 100-run statistics', 'connect sliders to run']
chk_conn = widget.CheckButtons(chk_conn_ax,
                               chk_conn_list,
                               [False, False])

btn_run_ax = plt.axes([0.825, 0.575, 0.125, 0.075])
btn_run = widget.Button(btn_run_ax, 'Run', color='lightskyblue', hovercolor='0.975')

btn_reset_ax = plt.axes([0.825, 0.5, 0.1, 0.04])
btn_reset = widget.Button(btn_reset_ax, 'Reset', color=widget_color, hovercolor='0.975')


# connect widgets
slide_mu.on_changed(slider_wrapper)
slide_sigma.on_changed(slider_wrapper)
btn_reset.on_clicked(reset)
btn_run.on_clicked(run_model)


# show the results
plt.show()
