from uetla.UETAnalytics import UETAnalytics
import sys
arg = sys.argv
import os;
filepath = os.path.dirname(os.path.realpath(__file__))

uet = UETAnalytics(filepath=filepath)
uet.createModel()