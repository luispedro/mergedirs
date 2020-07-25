# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    import sys
    sys.stderr.write('''\
Could not import `setuptools` module.

Please install it.

Under Ubuntu, it is in a package called `python-setuptools`.
''')
    sys.exit(1)

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
      author_email='luis@luispedro.org',
      url='http://luispedro.org/software/merge/',
      scripts = ['bin/mergedirs'],
      license='BSD',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'mergedirs.py = merge.merge:main',
          ],
      },
      )


