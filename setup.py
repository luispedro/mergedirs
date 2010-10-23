# -*- coding: utf-8 -*-
try:
    import setuptools
except ImportError:
    import sys
    print >>sys.stderr, '''\
Could not import `setuptools` module.

Please install it.

Under Ubuntu, it is in a package called `python-setuptools`.'''
    sys.exit(1)

from setuptools import setup, find_packages
__version__ = '0.1-git'

long_description='''
'''
classifiers = [
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    ]

setup(name='merge',
      version=__version__,
      description='Merge Directories',
      long_description=long_description,
      author='Luis Pedro Coelho',
      author_email='lpc@cmu.edu',
      url='http://luispedro.org/software/merge/',
      license='BSD',
      packages=find_packages(),
      )


