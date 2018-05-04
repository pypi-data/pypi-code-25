from setuptools import setup

setup(
	name='rpi_featureSelection',  # This is the name of your PyPI-package. 
	version= '0.0.1',  # Update the version number for new releases
	author='Keyi Liu, Zijun Cui, Qiang Ji',
	author_email='cuiz3@rpi.edu',
	url='https://www.ecse.rpi.edu/~cvrl/',
	description='RPI primitives using the latest 2018.4.18 APIs second submission',
	platforms=['Linux', 'MacOS'],
        keywords = 'd3m_primitive',
	entry_points = {
		'd3m.primitives': [
			'rpi_featureSelection.IPCMBplus_Selector = rpi_featureSelection.IPCMBplus_selector:IPCMBplus_Selector',
			'rpi_featureSelection.JMI_Selector = rpi_featureSelection.JMI_selector:JMI_Selector',
			'rpi_featureSelection.STMBplus_Selector = rpi_featureSelection.STMBplus_selector:STMBplus_Selector',
		],
	},
	packages=['rpi_featureSelection']
)
