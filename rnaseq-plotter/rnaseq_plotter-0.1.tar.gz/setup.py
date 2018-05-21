from setuptools import setup

setup(
    name='rnaseq_plotter',
    author='jlevy44',
    version='0.1',
    py_modules=['rnaseq_plotter'],
    install_requires=[
        'pandas',
	'numpy',
	'click',
        'seaborn',
        'scikit-learn',
        'multicoretsne',
        'plotly',
        'matplotlib'
    ],
    entry_points="""
        [console_scripts]
        rnaseq_plot=rnaseq_plotter:rnaseq"""
)
