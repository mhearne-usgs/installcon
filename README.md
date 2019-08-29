# installcon
Install conda packages in a conda virtual environment, make scripts/binaries always accessible via shell script wrappers

# Background

*installcon* is inspired by pipx (https://pipxproject.github.io/pipx/), and accomplishes roughly
the same goal - namely to install command line programs (in our case from conda packages instead of pip packages) without the user having to worry about where or how. *installcon* accomplishes this by liberal use of conda environments. It is *not* efficient in terms of disk space, but it does make installing conda-supplied command line packages easier.

# Installation

Steps:
 - `conda activate base`
 - `pip install git+https://github.com/mhearne-usgs/installcon.git`

 # Usage

 You can get command line help with installcon by typing:

 `installcon --help`

 ## Examples
 
 Install libcomcat:

 `installcon -p libcomcat -v 3.6`

 This will create a conda environment called *installcon_libcomcat* with a copy of the Python 3.6 interpreter, which will contain the scripts that libcomcat contains. It will also create shell script wrappers around each command. Output will look something like this:

<pre>
  Program: findid
    Description: Find the id(s) of the closest earthquake to input parameters.
    Path: /Users/mhearne/miniconda/bin/findid

  Program: getmags
    Description: Download epicenter and all contributed magnitudes in line format (csv, tab, etc.).
    Path: /Users/mhearne/miniconda/bin/getmags

  Program: getpager
    Description: Download PAGER exposure/loss results in line format (csv, tab, etc.).
    Path: /Users/mhearne/miniconda/bin/getpager

  Program: getphases
    Description: Download phase data for matching events into CSV or Excel format.
    Path: /Users/mhearne/miniconda/bin/getphases

  Program: getimpact
    Description: Download impact results in line format (csv, tab, etc.).
    Path: /Users/mhearne/miniconda/bin/getimpact

  Program: getproduct
    Description: Download product content files from USGS ComCat.
    Path: /Users/mhearne/miniconda/bin/getproduct

  Program: geteventhist
    Description: Print out ComCat event history.
    Path: /Users/mhearne/miniconda/bin/geteventhist

  Program: getcsv
    Description: Download basic earthquake information in line format (csv, tab, etc.).
    Path: /Users/mhearne/miniconda/bin/getcsv
</pre>

Note that certain packages may only work with certain versions of python. For example the *gmprocess* package, at the time of this writing, only works with python 3.6. You can sometimes determine this by using this command:

`conda search gmprocess`

The build column may have something that looks like *py36heacc8b8_1*. In this case, the *py36* is a clue to the version of Python that is supported.

To uninstall libcomcat, add the `-u` option:

`installcon -p libcomcat -u`

To see a listing of all the packages and their command line programs you have installed:

`installcon -p libcomcat -i`

<pre>
Package: libcomcat
  Program: findid
    Description: Find the id(s) of the closest earthquake to input parameters.
    Path: /Users/mhearne/miniconda/bin/findid
  Program: getmags
    Description: Download epicenter and all contributed magnitudes in line format (csv, tab, etc.).
    Path: /Users/mhearne/miniconda/bin/getmags
  Program: getpager
    Description: Download PAGER exposure/loss results in line format (csv, tab, etc.).
    Path: /Users/mhearne/miniconda/bin/getpager
  Program: getphases
    Description: Download phase data for matching events into CSV or Excel format.
    Path: /Users/mhearne/miniconda/bin/getphases
  Program: getimpact
    Description: Download impact results in line format (csv, tab, etc.).
    Path: /Users/mhearne/miniconda/bin/getimpact
  Program: getproduct
    Description: Download product content files from USGS ComCat.
    Path: /Users/mhearne/miniconda/bin/getproduct
  Program: geteventhist
    Description: Print out ComCat event history.
    Path: /Users/mhearne/miniconda/bin/geteventhist
  Program: getcsv
    Description: Download basic earthquake information in line format (csv, tab, etc.).
    Path: /Users/mhearne/miniconda/bin/getcsv
</pre>