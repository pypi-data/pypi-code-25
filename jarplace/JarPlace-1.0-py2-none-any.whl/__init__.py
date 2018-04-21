import os
from pathlib import Path

HOME = '%s/.jarplace' % str(Path.home())

if not os.path.exists(HOME):
    os.makedirs(HOME)
