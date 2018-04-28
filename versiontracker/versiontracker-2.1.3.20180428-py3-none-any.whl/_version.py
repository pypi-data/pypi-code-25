from datetime import datetime


__software_version__ = '2.1.3'
__data_date__ = datetime(year=2018, month=4, day=28)
__data_version__ = __data_date__.strftime('%Y%m%d')
__version__ = '{}.{}'.format(__software_version__, __data_version__)
