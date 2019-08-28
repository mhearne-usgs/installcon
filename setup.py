from distutils.core import setup
import versioneer


setup(name='installcon',
      description='Install conda binaries',
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='https://github.com/mhearne-usgs/installcon',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      packages=['installcon'],
      entry_points={
          'console_scripts': [
              'installcon = installcon.bin.installcon:main',
          ]
      }
      )
