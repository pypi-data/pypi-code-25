#   Imports
import os
import datetime
import setup

# Register this script
setup.scriptList.append('main.utils.py')

# Define Locations
pathBase = 'FrozenDesert'
pathUsers = 'FrozenDesert/Users'
pathInventory = 'FrozenDesert/Users/Inventory'
pathStats = 'FrozenDesert/Users/Stats'
pathLogs = 'FrozenDesert/Logs'
directoryMain = os.path.dirname(os.path.realpath(pathBase))
directoryUsers = os.path.dirname(os.path.realpath(pathUsers))
directoryUserStats = os.path.dirname(os.path.realpath(pathStats))
directoryUserInventory = os.path.dirname(os.path.realpath(pathInventory))
directoryLogs = os.path.dirname(os.path.realpath(pathLogs))

# other Variables
now = datetime.datetime.now()
sysTime = "[" + str(now.hour) + ":" + str(now.minute) + "] "
sysDate = "[" + str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "]"


# Define Functions

# Directory Creation
def makeDir(directoryName):
    if os.path.exists(directoryName):
        if os.path.isdir(directoryName):
            return False
    os.mkdir(directoryName)
    print(directoryName)
    writeFile(sysTime + " Created Directory: " + directoryName, sysDate + ".txt", pathLogs)
    return True


# File Creation
def makeFile(fileName, location):
    if os.path.exists(os.path.join(location, fileName)):
        if os.path.isfile(os.path.join(location, fileName)):
            return False
    if not os.path.exists(location):
        os.makedirs(location)
        os.chmod(location, 0o777)
    with open(os.path.join(location, fileName), "w+") as f:
        f.write("File Created: " + sysDate + "\n")
        print(fileName)
        f.close()
    return True


# Write To Files
def writeFile(text, fileName, location):
    with open(os.path.join(location, fileName), "a") as f:
        f.write("\n" + text)
        f.close()
    return True


# Clears Screen
def clearScreen():
    i = 0
    while i <= 50:
        print(" ")
        i += 1
