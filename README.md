# installcon
Install conda packages in a conda virtual environment, make scripts/binaries always accessible via shell script wrappers

# Background

*installcon* is inspired by pipx (https://pipxproject.github.io/pipx/), and accomplishes roughly
the same goal - namely to install command line programs (in our case from conda packages instead of pip packages) without the user having to worry about where or how. *installcon* accomplishes this by liberal use of conda *environments*. It is *not* efficient in terms of disk space, but it does make installing conda-supplied command line packages easier.

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
  Program: convertcwb
    Description: Convert a text file created by cutting/pasting Taiwan CWB PGA values from email into a text file.
    Path: /Users/mhearne/miniconda/bin/convertcwb

  Program: amps2xml
    Description: Convert a peak ground motion Excel file into ShakeMap input.
    Path: /Users/mhearne/miniconda/bin/amps2xml

  Program: gmunpack
    Description: Unpack directory or zip file containing ground motion data into a gmprocess/getstations friendly directory structure.
    Path: /Users/mhearne/miniconda/bin/gmunpack

  Program: getstations
    Description: Download, process, and create ground motion inputs for ShakeMap.
    Path: /Users/mhearne/miniconda/bin/getstations
</pre>

Note that certain packages may only work with certain versions of python. For example the *gmprocess* package, at the time of this writing, only works with python 3.6. You can sometimes determine this by using this command:

`conda search gmprocess`

The build column may have something that looks like *py36heacc8b8_1*. In this case, the *py36* is a clue to the version of Python that is supported.