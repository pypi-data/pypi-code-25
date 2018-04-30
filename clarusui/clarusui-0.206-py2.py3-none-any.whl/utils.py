import os
import webbrowser

def display(html):
    tempFileName = 'temp-element.html'
    with open(tempFileName, 'w') as f:
        f.write(html)
                    
    url = 'file://' + os.path.abspath(tempFileName)
    webbrowser.open(url)