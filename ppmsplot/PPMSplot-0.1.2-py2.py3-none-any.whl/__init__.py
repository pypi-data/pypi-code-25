from matplotlib import pyplot as plt


def plot(config, file_data):
    settings = config['plotSettings']
    fig, axis = plt.subplots(1, 1)

    # Grab titles
    if 'figureTitile' in settings  and settings['figureTitle']:
        plt.title(settings['figureTitle'])
    if 'xTitle' in settings  and settings['xTitle']:
        axis.set_xlabel(settings['xTitle'])
    if 'yTitle' in settings  and settings['yTitle']:
        axis.set_ylabel(settings['yTitle'])

    # Plot series
    for file in file_data:
        for series in file:
            axis.plot(
                series['x'], 
                series['y'],
                series['style'],
                label=series['label']
            )

    # Build legend
    if settings['legend']:
        plt.legend()

    # Build legend
    if settings['grid']:
        plt.grid(True)
    
    # If automatic border is set
    x_lims = [settings['xMin'], settings['xMax']]
    y_lims = [settings['yMin'], settings['yMax']]

    if settings['flipX']:
        x_lims = x_lims[::-1]
    if settings['flipY']:
        y_lims = y_lims[::-1]

    plt.xlim(x_lims)
    plt.ylim(y_lims)
  
    plt.savefig(settings['outputFilename'])
    plt.clf()





