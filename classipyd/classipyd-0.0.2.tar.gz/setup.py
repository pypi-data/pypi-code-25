from distutils.core import setup
setup(
    name='classipyd',
    packages=['classipyd'],
    version='0.0.2',
    long_description='''
# classipyd
Records a session while interactively allowing you to specify certain areas you would like to be redacted in the final video.

## How-To:
1. Run classipyd.py
 - When the program is run, you will havd ~2 seconds before the recording begins.
2. Capture/Flag desired areas on the screen.
 - See section on 'Controls' for more information.
3. `ctrl+space` will end the screen capture and beging the processing.
4. Run `<captured_{date}_{n}/clip.mp4>` to see your video.

## Controls

During the screenshot loop, you have the following controls:
- Pause/Unpause: `ctrl+shift`
- End Loop (begin processing): `ctrl+space`

Only while paused can you do the following commands to redact images:
- To Redact an image:
 1. Move cursor to top-left of desired area, press `esc`
 2. Move cursor to bottom-right of desired area, press `esc`
- To Flag an image and Redact relative to the flag:
 1. Press `<tic button>` to begin 'flagging mode'
 2. Move cursor to top-left of desired area to flag, press `esc`
 3. Move cursor to bottom-right of desired area to flag, press `esc`
 4. Move cursor to top-left of desired area to redact, press `esc`
 5. Move cursor to bottom-right of desired area to redact, press `esc`
    ''',
    long_description_content_type='text/markdown',
    author='Michael Cole',
    author_email='mcole2009@aol.com',
    license='MIT',
    url='https://github.com/mcole22266/classipyd',
    download_url='https://github.com/mcole22266/classipyd/archive/0.0.1.tar.gz',
    keywords=['redacting', 'screenshot', 'video', 'capture'],
    classifiers=[],
    install_requires=[
       'pyautogui',
       'time',
       'pathlib',
       'winsound',
       'PIL',
       'moviepy',
       'keyboard',
       'sys',
       'joblib',
       'multiprocessing',
       'shutil',
    ]
)

