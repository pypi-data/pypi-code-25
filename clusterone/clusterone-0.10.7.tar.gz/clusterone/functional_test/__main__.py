import logging

from .runner import run
from .getting_started_scenario import GettingStarted

logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S %p', level=logging.INFO)
run(GettingStarted)
