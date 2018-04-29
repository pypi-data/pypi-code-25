"""
Caissa voice-controlled personal assistant

@author: Dieter Dobbelaere
"""

import subprocess

def main():
    """Entry point for the application script"""
    # TODO: speech recognition
    subprocess.call(["mpg123", "http://icecast.vrtcdn.be/radio1-high.mp3"])

if __name__ == "__main__":
    main()
    