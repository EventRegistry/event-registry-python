from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='eventregistry',
      version='6.1.5',
      description = "A package that can be used to query information in Event Registry (http://eventregistry.org/)",
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: General',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Intended Audience :: Information Technology'
      ],
      url='https://github.com/gregorleban/EventRegistry',
      author='Gregor Leban',
      author_email='gregor@eventregistry.org',
      license='MIT',
      packages=['eventregistry'],
      install_requires=[
          'requests', 'six'
      ],
      zip_safe=False)
