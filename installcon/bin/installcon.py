#!/usr/bin/env python

import argparse
import sys
import shutil
import subprocess
import os.path
import json
import tarfile
from urllib import request
from io import BytesIO
import platform
import stat
import textwrap

PERMS = (stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR |
         stat.S_IXGRP | stat.S_IRGRP |
         stat.S_IXOTH | stat.S_IROTH)

# folder will be created under $HOME
INDEX_DIR = '.installcon'

# under INDEX_DIR, will contain database of installed scripts
INDEX_FILE = 'index.json'


def get_command_output(cmd):
    """
    Method for calling external system command.
    Args:
        cmd: String command (e.g., 'ls -l', etc.).
    Returns:
        Three-element tuple containing a boolean indicating success or failure,
        the stdout from running the command, and stderr.
    """
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    stdout, stderr = proc.communicate()
    retcode = proc.returncode
    if retcode == 0:
        retcode = True
    else:
        retcode = False
    return (retcode, stdout, stderr)


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass


def get_current_version():
    vinfo = sys.version_info
    version = '%i.%i' % (vinfo.major, vinfo.minor)
    return version


def install_package(package, pversion):
    # make sure conda package exists
    searchcmd = 'conda search %s' % package
    res, stdout, stderr = get_command_output(searchcmd)
    if not res:
        fmt = ('Could not find package "%s" in your list of current channels.'
               'Make sure this package exists and try again.\n Output from '
               'conda search:\n\n%s')
        desc = fmt % (package, stdout)
        return desc

    # now find a place in the user's path we can write to
    pathdirs = os.environ['PATH'].split(':')
    writeable = []
    for pathdir in pathdirs:
        if os.access(pathdir, os.W_OK):
            if 'envs' not in pathdir and 'condabin' not in pathdir:
                writeable.append(pathdir)
    if not len(writeable):
        desc = 'Could not find any directories in path we can write to.'
        return desc

    # this is where the shell scripts will go
    bindir = writeable[0]

    # make a marked name for the venv
    venv = 'installcon_%s' % package

    # next discover what all of the binaries/scripts are
    infocmd = 'conda search %s --info --json' % package
    res, stdout, stderr = get_command_output(infocmd)
    if not res:
        desc = 'Could not get information about the package.\n\n%s' % stdout
        return desc
    versions = json.loads(stdout)[package]
    last_version = versions[-1]
    tar_url = last_version['url']
    binaries = get_binaries(tar_url)

    # check to see if environment already exists
    # if so, remove it
    infocmd2 = 'conda info -e --json'
    res, stdout, stderr = get_command_output(infocmd2)
    if not res:
        fmt = 'Could not get information about installed environments.\n\n%s'
        desc = fmt % stdout
        return desc
    envdict = json.loads(stdout)
    hasenv = False
    for env in envdict['envs']:
        if venv in env:
            hasenv = True
            break
    if hasenv:
        print('Environment %s already exists, removing...' % venv)
        desc = remove_env(venv)
        print(desc)
        delete_from_index(venv)

    # create the environment
    installfmt = 'conda create -n %s python=%s %s -y'
    installcmd = installfmt % (venv, pversion, package)
    print('Creating the virtual environment with command: %s' % installcmd)
    print('This may take a while...')
    res, stdout, stderr = get_command_output(installcmd)
    if not res:
        fmt = ('Could not create virtual environment with the given '
               'version/package combination. Look at the error output '
               'below and/or consult with the developer '
               'to see what may be going on.\n\n%s')
        desc = fmt % stdout
        return desc

    # for each binary we identified, find it in our new venv
    # and make a shell script to call it.
    errors = []
    binary_list = []
    for binary in binaries:
        conda_path = os.environ['CONDA_PREFIX_1']
        binpath = os.path.join(conda_path, 'envs', venv, 'bin', binary)
        if not os.path.isfile(binpath):
            errors.append(binpath)
        scriptfile, sdesc = create_shell_script(binary, binpath, venv, bindir)
        binary_list.append({'name': binary,
                            'script_path': scriptfile,
                            'script_desc': sdesc})

    update_index(venv, binary_list)
    desc = 'You have installed the following scripts for %s:\n' % venv
    for venvdict in binary_list:
        desc += '\n  Program: %s\n' % (venvdict['name'])
        desc += '    Description: %s\n' % (venvdict['script_desc'])
        desc += '    Path: %s\n' % (venvdict['script_path'])

    return desc


def update_index(venv, binlist):
    # TODO - check to see if the input venv is already here, or
    # should this not happen?
    index_dir = os.path.join(os.path.expanduser('~'), INDEX_DIR)
    if not os.path.isdir(index_dir):
        os.mkdir(index_dir)
    indexfile = os.path.join(index_dir, INDEX_FILE)
    if os.path.isfile(indexfile):
        index = json.load(open(indexfile, 'rt'))
    else:
        index = {'packages': {}}
    index['packages'][venv] = binlist
    json.dump(index, open(indexfile, 'wt'))


def delete_from_index(venv):
    index_dir = os.path.join(os.path.expanduser('~'), INDEX_DIR)
    if not os.path.isdir(index_dir):
        os.mkdir(index_dir)
    indexfile = os.path.join(index_dir, INDEX_FILE)
    if os.path.isfile(indexfile):
        index = json.load(open(indexfile, 'rt'))
    else:
        return 'No index file exists.'
    # find the index of the venv in the list of packages
    if venv in index['packages']:
        del index['packages'][venv]
    json.dump(index, open(indexfile, 'wt'))
    return '%s deleted from index file.' % venv


def create_shell_script(binary, binpath, venv, bindir):
    # figure out what platform we're on, use to determine
    # name of bash config file
    if platform.system() == 'Darwin':
        bashrc = 'bash_profile'
    else:
        bashrc = 'bashrc'
    template = '''
    #!/usr/bin/env sh

    source ~/.%s
    conda activate %s

    cmd="%s $@"
    eval $cmd
    '''
    script_text = textwrap.dedent(template % (bashrc, venv, binpath))
    scriptfile = os.path.join(bindir, binary)
    with open(scriptfile, 'wt') as f:
        f.write(script_text)
    os.chmod(scriptfile, PERMS)

    # get the first paragraph of the help from the new script
    cmd = '%s --help' % scriptfile
    res, stdout, stderr = get_command_output(cmd)
    tdesc = stdout.decode('utf-8').split('\n\n')[1]
    desc = ' '.join(tdesc.split('\n'))
    return (scriptfile, desc)


def remove_env(venv):
    removecmd = 'conda remove --name %s --all -y' % venv
    res, stdout, stderr = get_command_output(removecmd)
    if not res:
        desc = 'Unable to remove previous environment. \n\n%s' % stdout
        return desc

    return 'Removed environment %s' % venv


def get_binaries(tar_url):
    binaries = []
    response = request.urlopen(tar_url)
    fileobj = BytesIO(response.read())
    response.close()
    tfile = tarfile.open(fileobj=fileobj, mode='r:bz2')
    for name in tfile.getnames():
        if name.startswith('bin') or name.startswith('python-scripts'):
            fdir, binary = name.split('/')
            binaries.append(binary)
    tfile.close()
    return binaries


def delete_scripts(venv):
    desc = ''
    index_dir = os.path.join(os.path.expanduser('~'), INDEX_DIR)
    indexfile = os.path.join(index_dir, INDEX_FILE)
    if not os.path.isfile(indexfile):
        desc = 'No index file exists.'
        return desc
    index = json.load(open(indexfile, 'rt'))
    binlist = index['packages'][venv]
    for bindict in binlist:
        bname = bindict['name']
        bpath = bindict['script_path']
        os.remove(bpath)
        desc += 'Deleted wrapper script %s\n' % bname

    return desc


def remove_package(package):
    venv = 'installcon_%s' % package
    print('Deleting virtual environment %s...' % venv)
    desc1 = remove_env(venv)

    # delete wrapper scripts
    print('Deleting wrapper scripts...')
    desc2 = delete_scripts(venv)

    print('Deleting %s from index...' % venv)
    desc3 = delete_from_index(venv)

    return '\n'.join([desc1, desc2, desc3])


def list_packages():
    index_dir = os.path.join(os.path.expanduser('~'), INDEX_DIR)
    indexfile = os.path.join(index_dir, INDEX_FILE)
    if not os.path.isfile(indexfile):
        desc = 'No index file exists.'
        return desc
    index = json.load(open(indexfile, 'rt'))
    desc = ''
    for venv, binlist in index['packages'].items():
        _, package = venv.split('_')
        desc += '\nPackage: %s\n' % package
        for bindict in binlist:
            desc += '  Program: %s\n' % bindict['name']
            desc += '    Description: %s\n' % bindict['script_desc']
            desc += '    Path: %s\n' % bindict['script_path']
    return desc


def main():
    desc = '''Install binaries from conda packages into user's path,
    or list installed binaries.

    If a conda package provides command line utilities which you would find
    useful, but don't want to install into an existing Python environment or
    fuss with creating and managing separate python environments, this tool
    will do that for you.

    This program can:
     - Install programs by:
       - Installing input conda package into a custom conda virtual environment
       - Discovering binaries and python scripts provided by that conda package
       - Making bash shell script wrappers for each binary
       - Installing those wrappers in a writable directory in user's path,
         OR
       - Creating a $HOME/bin directory and install wrappers there.
    - List installed programs by conda package and environment.

    Examples:

    To install libcomcat into a Python 3.6 environment:

    installcon -p libcomcat -v 3.6

    To install amptools:

    installcon -p amptools -v 3.6

    '''
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=CustomFormatter,)
    parser.add_argument('--package', '-p',
                        help='Conda package available in your conda channels')
    phelpstr = ('python version to install into conda environment '
                '(defaults to current).')
    parser.add_argument('--version', '-v', default=get_current_version(),
                        help=phelpstr)
    ihelpstr = '''List binaries already installed, and the packages
    and virtual environments to which they belong.
    '''
    parser.add_argument('--index', '-i', help=ihelpstr, action='store_true')
    parser.add_argument('--uninstall', '-u', action='store_true',
                        help='Uninstall binaries from package')
    args = parser.parse_args()

    if shutil.which('conda') is None:
        msg = ('Conda does not seem to be in your path. Install it '
               'and then re-install this program.')
        print(msg)
        sys.exit(0)

    if args.index:
        desc = list_packages()
        print(desc)
        sys.exit(0)

    if args.package:
        if args.uninstall:
            desc = remove_package(args.package)
        else:
            desc = install_package(args.package, args.version)
    print(desc)


if __name__ == '__main__':
    main()
