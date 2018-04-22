from distutils.core import setup
import sys

setup(
    name='pyinputedittext',
    packages=['pyinputedittext'],  # this must be the same as the name above
    python_requires='>=3',
    install_requires=["pywin32==223"] if sys.platform.startswith("win") else [],
    version='1.0',
    description='Cross-platform package that allows editing text in console',
    author='Lyubomir Rumenov',
    author_email='lubeto3099@gmail.com',
    url='https://github.com/Def4l71diot/pyinputedittext',
    download_url='https://github.com/Def4l71diot/pyinputedittext/archive/1.0.tar.gz',
    keywords=['linux', 'windows', 'macos', 'unix', 'console', 'input', 'development'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
    ]
)
