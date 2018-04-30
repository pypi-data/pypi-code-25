# Imports
from main import utils
import setup

# Register this script
setup.scriptList.append('main.bootUp.py')


# Make Log File
utils.makeFile(utils.sysDate + ".txt", utils.pathLogs)

# Make Main Directory
utils.makeDir(utils.pathBase)
# Make Users Directory
utils.makeDir(utils.pathUsers)
# Make Logs Directory
utils.makeDir(utils.pathLogs)
# Make Inventory Directory
utils.makeDir(utils.pathInventory)
# Make Stats Directory
utils.makeDir(utils.pathStats)


# Make Files

# Clears Screen
utils.clearScreen()

