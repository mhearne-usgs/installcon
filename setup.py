from distutils.core import setup

setup(name='installcon',
      description='Install conda binaries',
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='https://github.com/mhearne-usgs/installcon',
      packages=['installcon'],
      entry_points={
          'console_scripts': [
              'installcon = installcon.bin.installcon:main',
          ]
      }
      )
