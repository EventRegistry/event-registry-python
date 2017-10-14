from setuptools import setup
import re

VERSIONFILE = "eventregistry/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='eventregistry',
      version = verstr,
      description = "A package that can be used to query information in Event Registry (http://eventregistry.org/)",
      classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: General',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Intended Audience :: Information Technology'
      ],
      url = 'https://github.com/EventRegistry/event-registry-python',
      author = 'Gregor Leban',
      author_email = 'gregor@eventregistry.org',
      license = 'MIT',
      packages = ['eventregistry'],
      install_requires = [
          'requests', 'six', 'pytz'
      ],
      zip_safe=False)
