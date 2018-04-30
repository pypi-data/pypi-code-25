#Imports
import time
from main import utils

# Register this script
setup.scriptList.append('main.userIdentification.py')

# Request User Input
print('Welcome To The Frozen Desert. Would You Like To Register Or Sign In?')
print(" ")

while True:
    # Store User Input
    identity = input("Login [L] / Register [R]: ")

    # Checks To See If The Answer Is Appropriate
    if identity.lower() not in ('l', 'r'):
        continue
    print(" ")
    break

#TODO: Make Te Login & Registration Functions Work

# Begins User Login
if identity.lower() == "l":
    print("Opening Login Pane")
    time.sleep(1)
    # Clears Screen
    utils.clearScreen()

#Begins User Registration
if identity.lower() == "r":
    print("Opening Registration Pane")
    # Clears Screen
    utils.clearScreen(0)
