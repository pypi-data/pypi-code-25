# flake8: noqa
from dvina.active_labeler import ActiveLabeler
from dvina.csv_data_provider import CsvDataProvider
from dvina.basic_data_processor import DataProcessor, BasicDataProcessor
from dvina.logger_configurator import LoggerConfigurator
import logging

__version__ = '1.0'

# The user, not the library, dictates what happens when a logging event occurs.
# Adding default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
