from setuptools import setup

setup(
    name='qm_scripts',
    version='0.1.1',
    description='A set of scripts useful for analyzing outputs and setup inputs in quantum chemistry',
    license='GPL',
    url='https://github.com/iinfant76/qm_scripts',
    author=['Ivan Infante'],
    author_email='iinfant76@gmail.com',
    keywords='MD cp2k',
    packages=[
        "general"],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)', 
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Chemistry'
    ],
    install_requires=[
        'numpy', 'matplotlib', 'scipy', 'qmflows'], 
    scripts=[
        'cp2k_md/xyz2pdb.py',
        'cp2k_md/xyz2psf.py']
)

