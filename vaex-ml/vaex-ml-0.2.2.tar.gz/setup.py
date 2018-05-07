from setuptools import setup
import sys, os, imp

import sys, os, imp
from setuptools import Extension
from setuptools.command.develop import develop


dirname = os.path.dirname(__file__)
path_version = os.path.join(dirname, "vaex/ml/_version.py")
version = imp.load_source('version', path_version)

name        = 'vaex'
author      = "Maarten A. Breddels"
author_email= "maartenbreddels@gmail.com"
license     = 'MIT'
version     = version.__version__
url         = 'https://www.github.com/maartenbreddels/vaex'
install_requires_ml = ['vaex-core', 'numba']

class DevelopCmd(develop):
    def run(self):
        super(DevelopCmd, self).run()
        import vaex

        source = os.path.abspath(os.path.join('vaex', 'ml'))
        target = os.path.abspath(os.path.join(os.path.dirname(vaex.__file__), 'ml'))
        if not os.path.exists(target):
            print("*** extra: linking ", source, "->", target)
            os.symlink(source, target)


setup(name=name+'-ml',
    version=version,
    description='Machine learning support for vaex',
    url=url,
    author=author,
    author_email=author_email,
    install_requires=install_requires_ml,
    license=license,
    packages=['vaex.ml'],
    include_package_data=True,
    zip_safe=False,
    cmdclass={'develop': DevelopCmd},
    entry_points={'vaex.namespace': ['ml = vaex.ml:add_namespace']}
    )
