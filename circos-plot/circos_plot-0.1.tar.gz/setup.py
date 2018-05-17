from setuptools import setup

setup(
    name='circos_plot',
    version='0.1',
    py_modules=['circos_plot'],
    install_requires=[
        'numpy',
        'click'
    ],
    entry_points="""
        [console_scripts]
        circos_plotter=circos_plot:circosplot"""
)