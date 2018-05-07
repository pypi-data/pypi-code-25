from setuptools import setup


setup(name="SeleniumFramework",
      version="0.1.8",
      description="Backend for run test suites from json definition files",
      author="Julio Reyes",
      author_email="julio@truetech.com",
      scripts=["Suite.py","Test.py", "BaseTest.py", "Action.py", "MSDBConnect.py", "Request.py", "Setup.py"],
      requires=['selenium', 'pymssql', 'requests'],
      py_modules=["BaseTest", "Action", "MSDBConnect", "Request"],
      install_requires=['selenium', 'pymssql', 'requests'],
      python_requires='>3.6',
      data_files=[('.', ['chromedriver.exe', 'geckodriver.exe', 'MicrosoftWebDriver.exe'])]
      )
