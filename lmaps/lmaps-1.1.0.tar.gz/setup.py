import setuptools
try: import multiprocessing
except ImportError: pass
setuptools.setup(setup_requires=['pbr>=3.0.0,<4.0.0'],pbr=True)