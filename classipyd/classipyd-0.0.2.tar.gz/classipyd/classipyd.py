#! python
# classipyd.py - Use Screen Capture to record a session while interactively
#                redacting desired areas of the screen - End producted is a 
#                video (mp4) with black boxes of redacted areas. 
# Author: Michael Cole
# Date: 5-3-2018

import pyautogui as pag
import time
from pathlib import Path
from winsound import Beep
from PIL import Image, ImageDraw, ImageFile
import moviepy.editor as mpy
import keyboard
import sys
from joblib import Parallel, delayed
from joblib.pool import has_shareable_memory
import multiprocessing

import shutil

# Global Variables ============================================================
TIMESTAMP= time.ctime()
WEEKDAY, MONTH, DAY, TIME, YEAR = TIMESTAMP.split()
FPS = 10
filepath = None
directorypath = None

ImageFile.LOAD_TRUNCATED_IMAGES = True

flag_redact_dict = {} # key = flag / value = dx, dy, w, h


def doublebeep():
    for _ in range(2):
        Beep(600, 75)
        sys.stdout.flush()

def singlebeep():
    Beep(750, 200)
    sys.stdout.flush()

def singlebeep_lite():
    Beep(800, 50)
    sys.stdout.flush()

def doublebeep_lite():
    for _ in range(2):
        Beep(800, 50)
        sys.stdout.flush()

def time_it(function):
    '''Used for testing purposes'''
    start = time.time()
    function()
    end = time.time() 
    total = end - start
    print(f'TIME: {total} seconds')

# Create directories ==========================================================
def create_directories():
    '''Sets up directory paths that will be used to store screenshots and 
    redacted images.'''
    global filepath, directorypath
    filepath = Path.cwd() 
    counter = 1
    directorypath = Path(f'{filepath}/captured_{YEAR}{MONTH}{DAY}_{counter}')
    while directorypath.exists():
        directorypath = Path(f'{filepath}/captured_{YEAR}{MONTH}{DAY}')
        counter += 1
        directorypath = Path(f'{directorypath}_{counter}')

    # File Tree
    Path.mkdir(directorypath)
    Path.mkdir(directorypath/'screenshots')
    Path.mkdir(directorypath/'redacted_images')   

# Create and save screenshots =================================================
def record_screenshots():
    '''Creates a loop that continually stores screenshots with functionality:
    - Pause: <ctrl+shift>
    - Finish: <ctrl+space>
    - Capture point: <esc>
    - Start flagging mode: <`>
    '''
    global directorypath, flag_redact_dict
    # start with two second delay to allow user to prepare
    time.sleep(2)
    print()
    print('== Begin recording == ')
    doublebeep()

    # loop creating screenshots
    counter = 1
    redacted_counter = 0
    done = False
    paused = False
    while not done and not counter > 9999:
        if not paused: 
            if keyboard.is_pressed('ctrl+space'): # end loop
                done = True
            if keyboard.is_pressed('ctrl+shift'): # pause loop
                paused = not paused
                singlebeep()
                print('paused')
                time.sleep(0.2)
            else:
                # Continue screenshots
                str_counter = str(counter).rjust(4, '0')
                filename = Path(f'{directorypath}/screenshots/screenshot_{str_counter}.png')
                pag.screenshot(filename)
                if counter % 10 == 0:
                    print('Recording screen activity')
                counter += 1
        elif paused:
            if keyboard.is_pressed('ctrl+shift'): # unpause loop
                singlebeep_lite()
                paused = not paused
                singlebeep()
                print('unpaused')
                time.sleep(0.2)
            if keyboard.is_pressed('esc'):       # capture top-left of redacted image
                redacted_counter += 1
                str_redacted_counter = str(redacted_counter).rjust(2, '0')
                x1, y1 = pag.position()
                print('topleft: ({},{})'.format(x1, y1))
                singlebeep_lite()
                time.sleep(0.2)
                keyboard.wait('esc')            # capture bottom-right of redacted image
                x2, y2 = pag.position()
                w, h = x2-x1, y2-y1
                time.sleep(0.2)
                print('bottomright: ({},{})'.format(x2,y2))
                singlebeep_lite()
                redacted_name = f'img{str_redacted_counter}.png'
                pag.screenshot(f'{directorypath}/redacted_images/{redacted_name}', 
                        (x1,y1,w,h))
                flag_redact_dict[redacted_name] = (0, 0, w, h) 
                print(f'Created redacted image {redacted_counter}')
            if keyboard.is_pressed('`'):       # switch to 'flagging' mode
                singlebeep_lite()
                print('Flagging --')
                redacted_counter += 1
                str_redacted_counter = str(redacted_counter).rjust(2, '0')
                keyboard.wait('esc')           # capture top-left of flagged image
                x1, y1 = pag.position()
                print('topleft: ({},{})'.format(x1, y1))
                singlebeep_lite()
                time.sleep(0.2)
                keyboard.wait('esc')           # capture bottom-right of flagged image
                x1_, y1_ = pag.position()
                w1, h1 = x1_-x1, y1_-y1
                time.sleep(0.2)
                print('bottomright: ({},{})'.format(x1_, y1_))
                singlebeep_lite()
                flagged_name = f'img{str_redacted_counter}.png'
                pag.screenshot(f'{directorypath}/redacted_images/{flagged_name}',
                        (x1,y1,w1,h1))
                print(f'Created flagged image {redacted_counter}')
                print('Redacting --')
                keyboard.wait('esc')          # capture top-left of relative redacted image
                x2, y2= pag.position()
                dx1, dy1 = x2-x1, y2-y1 
                print('topleft: ({},{})'.format(x2, y2))
                singlebeep_lite()
                time.sleep(0.2)
                keyboard.wait('esc')          # capture bottom-right of relative redacted image
                x3, y3= pag.position()
                w2, h2= x3-x2, y3-y2
                dx2, dy2 = x3-x1, y3-y1 
                time.sleep(0.2)
                print('bottomright: ({},{})'.format(x3, y3))
                doublebeep_lite()
                flag_redact_dict[flagged_name] = (dx1, dy1, dx2, dy2)
                print('Coordinates Saved')
                print(dx1, dy1, dx2, dy2)
            if keyboard.is_pressed('ctrl+space'):  # end loop
                done = True


# Processing ==================================================================

def process_screenshot(screenshot, redactedlist, num_screenshots):
    '''Searches for each image in the redacted directory within each screenshot
    then redacts the images according to flag_redact_dic.
    '''
    global directorypath, flag_redact_dict, counter
    for redacted in redactedlist:
        image = Image.open(screenshot)
        draw = ImageDraw.Draw(image)
        redacted_name = redacted.name
        redacted_str = str(redacted)
        while pag.locate(redacted_str, image, grayscale=True): 
            x, y, w, h = pag.locate(redacted_str, image, grayscale=True)
            dx1, dy1, dx2, dy2 = flag_redact_dict[redacted_name]
            x1, y1 = x+dx1, y+dy1
            x2, y2 = x+dx2, y+dy2 
            draw.rectangle([x1, y1, x2, y2], fill='black')
            draw.point((x+1, y+1), 'black') # to ensure loop isn't infinite
            draw.point((x+2, y+2), 'white') # to ensure loop isn't infinite
            image.save(screenshot)          # overwrites original screenshot with 
                                            # redactions.  Update later to 
                                            # keep originals.
        image.close()
    counter += 1
    print("Completed image {} of {}".format(counter, num_screenshots))


counter = 0
def process_parallel():
    '''Uses joblib to use all available cores to process each image.  Each core is
    given a screenshot that is then processed via process_screenshot'''
    global directorypath, flag_redact_dict, counter
    screenshotlist = [str(screenshot) for screenshot in Path.iterdir(directorypath/'screenshots')]
    redactedlist = [redacted for redacted in Path.iterdir(directorypath/'redacted_images')]
    doublebeep()
    print()
    print('== Processing ==')
    num_screenshots = len(screenshotlist)
    num_cores = multiprocessing.cpu_count()
    with Parallel(n_jobs=num_cores, backend='threading') as parallel:
#      counter += 1
#      counter_str = str(counter).rjust(4, '0')
#      parallel(delayed(process_screenshot)(screenshot, redactedlist, counter_str, num_screenshots) for screenshot in screenshotlist)
       parallel(delayed(process_screenshot)(screenshot, redactedlist, num_screenshots) for screenshot in screenshotlist)
    print()
    print('Done')


def process_regular():
    '''Depracated and replaced with process_parallel as any benefits to processing
    the brute force way was minimal.  Parallel processing proved to be a better option.'''
    doublebeep()
    print()
    print('== Processing ==')
 
    # Redact specified image
    screenshotlist = [str(screenshot) for screenshot in Path.iterdir(directorypath/'screenshots')]
    redactedlist = [str(redacted) for redacted in Path.iterdir(directorypath/'redacted_images')]
 
    num_screenshots = len(screenshotlist)
    counter = 0
 
    for screenshot in screenshotlist:
        counter += 1
        counter_str = str(counter).rjust(4, '0')
        redact_str = (f'Redacting screenshot {counter} of {num_screenshots}...')
        print(redact_str, end='')
        for redacted in redactedlist:
            process_screenshot(screenshot, redacted, counter_str)
        print('\b' * len(redact_str), end='')
    print()
    print('Done')
 

# Create clip =================================================================
def create_clip():
    '''Creates a clip out of all images in the screenshot directory and makes an 
    mp4 file'''
    global directorypath    
    print()
    print()
    print('== Creating clip ==')
    screenshotlist = [str(screenshot) for screenshot in Path.iterdir(directorypath/'screenshots')]
    clip = mpy.ImageSequenceClip(screenshotlist, fps=FPS)
    clip.write_videofile(f'{directorypath}/clip.mp4', fps=FPS)
    print()
    print('== Complete! ==')

def main():
    '''Main function that runs the entire program''' 
    create_directories()
    record_screenshots()
    process_parallel()
    create_clip()

# Run Program =================================================================
if __name__ == '__main__':
    main()
    
