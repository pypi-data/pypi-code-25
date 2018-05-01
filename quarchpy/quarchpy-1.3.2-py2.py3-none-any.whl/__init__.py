import os, sys
import inspect

## Adds / to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /connection_specific to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//connection_specific")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /device_specific to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//device_specific")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /serial to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//connection_specific//serial")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /QIS to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//connection_specific//QIS")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

## Adds /usb_libs to the path.
folder2add = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]) + "//connection_specific//usb_libs")
if folder2add not in sys.path:
    sys.path.insert(0, folder2add)

from device import *

current_path = os.path.dirname(os.path.abspath(__file__))

## Import all the modules in /device_specific.
for name in os.listdir(current_path +"//device_specific"):
    if name.endswith(".py"):
         # Strip the extension.
         module = name[:-3]
         # Import.
         exec("from device_specific." + module + " import *")

from connection import startLocalQIS