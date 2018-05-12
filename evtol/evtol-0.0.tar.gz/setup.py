from setuptools import setup

setup(name="evtol",
        version="0.0",
        description="Fixed wing - VTOL Sizing module",
        author="Rano Veder, Lorenzo Terenzi, Jose Ignacio de Alvear Cardenas",
        license="",
        packages=['evtol'], 
        test_suite='nose.collector',
        tests_require=['nose', 'nose-cover3'])