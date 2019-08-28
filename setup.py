from distutils.core import setup

setup(name='installcon',
      description='Install conda binaries',
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='https://github.com/mhearne-usgs/installcon',
      packages=['bin'],
      entry_points={
          'console_scripts': [
              'installcon = bin.installcon:main',
          ]
      }
      )
