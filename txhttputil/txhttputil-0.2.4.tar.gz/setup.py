from setuptools import setup

package_name = "txhttputil"
package_version = '0.2.4'

requirements = ["pytz"]

setup(
    name='txhttputil',
    packages=['txhttputil', 'txhttputil.downloader', 'txhttputil.login_page',
              'txhttputil.site', 'txhttputil.util'],
    package_data={'txhttputil.login_page': ['*.xml']},
    version=package_version,
    install_requires=requirements,
    description='Synerty utility classes for serving a static site with twisted.web with user permissions.',
    author='Synerty',
    author_email='contact@synerty.com',
    url='https://github.com/Synerty/txhttputil',
    download_url=('https://github.com/Synerty/%s/tarball/%s'
                  % (package_name, package_version)),
    keywords=['twisted', 'resource', 'file', 'download', 'synerty'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
)
