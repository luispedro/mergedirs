from setuptools import setup

exec(compile(open('mergedirs/mergedirs_version.py').read(),
             'mergedirs/mergedirs_version.py', 'exec'))

long_description = open('README.md', encoding='utf-8').read()

classifiers = [
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    ]

setup(name='mergedirs',
      version=__version__,
      description='Merge directories without losing files',
      long_description=long_description,
      long_description_content_type='text/markdown',
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


