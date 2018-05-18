import os, subprocess, sys, time
from setuptools import setup, find_packages

RELEASE = "0.9.0"

if sys.version_info.major > 2: raise Exception("Only works well on Python 2.7, using PyPy2-6.0 is recommended")

lt = time.localtime()
version = (lt.tm_year, (10 + lt.tm_mon) * 100 + lt.tm_mday, (10 + lt.tm_hour) * 100 + lt.tm_min)
versionString = '.'.join(map(str, version))
if 'build' in sys.argv:
  if os.path.exists(".git"):  # must be local development, but ignored
    try:
      so, se = subprocess.Popen("git describe --always", shell = sys.platform != 'win32', bufsize = 1, stdout = subprocess.PIPE).communicate()  # use tag or hash
      extra = so.strip().decode(sys.stdout.encoding).replace("\n", "-")
      if "\x0d" in extra: extra = extra.split("\x0d")[1]
      print("Found Git hash %s" % extra)
    except: extra = "svn"
  else: extra = "svn"  # in case this is checked out and built not from Github
  with open("rsyncr%sversion.py" % os.sep, "w") as fd:  # create version string at build time
    fd.write("""\
__version_info__ = ({version[0]}, {version[1]}, {version[2]})
__version__ = r'{fullName}'
__release_version__ = '{release}'
""".format(version = version, fullName = versionString + "-" + extra, release = RELEASE))

# Clean up old binaries for twine upload
if os.path.exists("dist"):
  rmFiles = list(sorted(os.listdir("dist")))
  for file in (f for f in rmFiles if any([f.endswith(ext) for ext in (".tar.gz", "zip")])):
    print("Removing old sdist archive %s" % file)
    try: os.unlink(os.path.join("dist", file))
    except: print("Cannot remove old distribution file " + file)

setup(
  name = 'rsyncr',
  version = versionString,  # without extra
  description = "rsyncr - An enhanced rsync backup wrapper script",
  long_description = "",  # TODO
  install_requires = ["textdistance >= 3"],  # actually an optional dependency
  classifiers = [c.strip() for c in """
        Development Status :: 5 - Production/Stable
        Intended Audience :: Science/Research
        Intended Audience :: System Administrators
        License :: OSI Approved :: GNU General Public License v3 (GPLv3)
        Operating System :: OS Independent
        Programming Language :: Python
        Programming Language :: Python :: 2
        Programming Language :: Python :: 2.7
        """.split('\n') if c.strip()],  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
  keywords = 'rsync wrapper backup safety feedback UI interface',
  author = 'Arne Bachmann',
  author_email = 'ArneBachmann@users.noreply.github.com',
  maintainer = 'Arne Bachmann',
  maintainer_email = 'ArneBachmann@users.noreply.github.com',
  url = 'http://github.com/ArneBachmann/rsyncr',
  license = 'GNU General Public License v3 (GPLv3)',
  packages = ["rsyncr"],
#  package_dir = {"": ""},
#  package_data = {"": ["check.py", "run.py"]},
  include_package_data = False,  # if True, will *NOT* package the data!
  zip_safe = False,
  entry_points = {
    'console_scripts': [
      'rsyncr=rsyncr.run:main'
    ]
  },
)
