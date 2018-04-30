from ctypes import windll

TWENTY_ONE_BY_NINE_RESIZE = (168, 72)
SIXTEEN_BY_NINE_RESIZE = (128, 72)

def get_screen_resolution():
    return (windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1))


def get_transformed_ratio():
    """
    Returns a tuple based on the screen ratio, to be used when resizing the image on the screen
    """

    width, height = get_screen_resolution()
    
    if width/height == 16/9:
        return SIXTEEN_BY_NINE_RESIZE
    elif width/height == 21/9:
        return TWENTY_ONE_BY_NINE_RESIZE
    else:
        return SIXTEEN_BY_NINE_RESIZE

