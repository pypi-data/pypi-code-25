from setuptools import setup

setup(name="booleantools",
      version="0.3.2.1",
      description="A library for boolean functions, functions on GF(4), and Cellular Automata",
      url=None,
      author="Wesley Rogers, Andrew Penland",
      author_email="wsrogers3@catamount.wcu.edu",
      license="MIT",
      python_requires=">=3",
      packages = ["booleantools", "booleantools.fields", "booleantools.cellularautomata"],
      zip_safe=False)
