from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='eventregistry',
      version='6.0',
      long_description=readme(),
      classifiers=[
        'Development Status :: 2 - Besta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Information extraction',
      ],
      url='http://github.com/storborg/funniest',
      author='Gregor Leban',
      author_email='gleban@gmail.com',
      license='MIT',
      packages=['eventregistry'],
      zip_safe=False)