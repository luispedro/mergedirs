# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

exec(compile(open('mergedirs/mergedirs_version.py').read(),
             'mergedirs/mergedirs_version.py', 'exec'))

long_description = open('README.md', encoding='utf-8').read()

classifiers = [
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    ]

setup(name='merge',
      version=__version__,
      description='Merge directories without losing files',
      long_description=long_description,
      author='Luis Pedro Coelho',
      author_email='luis@luispedro.org',
      url='https://luispedro.org/software/merge/',
      license='BSD',
      packages=['mergedirs'],
      entry_points={
          'console_scripts': [
              'mergedirs = mergedirs.merge:main',
          ],
      },
      )


