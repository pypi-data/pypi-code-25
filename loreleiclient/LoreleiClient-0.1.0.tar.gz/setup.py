from setuptools import setup, find_packages
	  
setup(name='LoreleiClient',
      version='0.1.0',
      description='The text based MUD made by Lorinthio',
      author='Lorinthio',
      author_email='benrandallswg@gmail.com',
      packages=find_packages(),
      install_requires=[
          'twisted',
          'pygame',
		  'LoreleiLib'
      ],
      zip_safe=False)