import os
sep = os.sep
base_path = os.path.dirname(__file__)
logs_path = "{base}{sep}logs{sep}".format(base=base_path, sep=sep)
tests_path = "{base}{sep}tests{sep}".format(base=base_path, sep=sep)
