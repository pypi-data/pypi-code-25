from setuptools import setup


setup(
    name='lsst-sphinx-bootstrap-theme',
    description=(
        "Sphinx theme for LSST user documentation built on Bootstrap and "
        "Astropy's theme."
    ),
    author='Association of Universities for Research in Astronomy',
    author_email='jsick@lsst.org',
    license='BSD',
    url='https://github.com/lsst-sqre/lsst-sphinx-bootstrap-theme',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: Sphinx :: Theme',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False,
    packages=['lsst_sphinx_bootstrap_theme'],
    package_data={'lsst_sphinx_bootstrap_theme': [
        'theme.conf',
        '*.html',
        'static/*.css',
        'static/*.js',
        'static/*.ico',
        'static/*.svg',
        'static/*.png',
        'templates/autosummary/*.rst'
    ]},
    include_package_data=True,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
)
