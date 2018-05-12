"""
This module runs on the base system as a Python script

The module mainly discovers the existing conda environments and sends
the source code over to the target system for further processing.

NOTE:
    The script should be compatible with both Python 2 and 3. It will
    be executed using whichever version of Python is available using
    ``python`` command.
"""

import argparse
import base64
from io import BytesIO
import json
import os
import subprocess
import sys
import zipfile

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

HOST = None
PORT = None


def parse_args():
    """Parse the command line arguments when run as a script

    Return:
        An argparse.Namespace instance for the parsed arguments
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-z', '--zip', default=False, action='store_true',
                            help='Create a zip file for transferring later')
    arg_parser.add_argument('-n', '--name', default=None, action='store',
                            help='Name of the software to migrate')
    arg_parser.add_argument('-d', '--dir', default=None, action='store',
                            help='Directory containing the software')
    return arg_parser.parse_args()



def get_conda_env(env=None):
    """Return the yml file of current conda environment

    The function runs a subprocess to get the yml file of the current
    conda environment. The results of the subprocess are returned as
    a tuple and if the yml file was obtained, it will be index 1 of
    the tuple.

    Kwargs:
        :env=None: Conda environment to source, if not the currently
            active environment.

    Return:
        A tuple whose elements are a boolean indicating whether the
        process ran error free, the stdout of the process and the
        stderr of the process
    """
    source_cmd = 'source ./activate %s &&' % env if env is not None else ''
    proc = subprocess.Popen('%s conda env export --no-builds' % source_cmd,
                            shell=True, universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return (not bool(proc.returncode)), out, err


def get_conda_min_deps(env, source_env=False):
    """Try to create a list of minimal dependencies to install

    The function queries the conda environment for all dependencies and
    then tries to determine the which dependencies are sub-dependencies of
    others. In this way, a minimal list of dependencies is created.

    Args:
        :env: The name of the conda environment to query

    Kwargs:
        :source_env=False: Boolean indicator whether to source conda env
            before getting data or not

    Return:
        A list of conda package objects if succesful, or None
        if the conda envrionment could not be loaded
    """
    source_cmd = 'source ./activate %s &&' % env if source_env else ''
    proc = subprocess.Popen('%s conda list --json' % source_cmd,
                            shell=True, universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        sys.stderr.write(err)
        return None

    all_deps = json.loads(out)
    min_deps = [dep for dep in all_deps]

    for dep in all_deps:
        if dep not in min_deps:
            continue
        proc = subprocess.Popen("%s conda create --dry-run --json -n dummy %s=%s=%s"
                                % (source_cmd, dep['name'], dep['version'], dep['build_string']),
                                shell=True, universal_newlines=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            continue
        sub_deps = []
        actions = json.loads(out)['actions']
        if isinstance(actions, dict):
            sub_deps.extend(actions['LINK'])
        else:
            for action in actions:
                sub_deps.extend(action['LINK'])
        for sub_dep in sub_deps:
            if sub_dep in min_deps and sub_dep != dep:
                min_deps.remove(sub_dep)
    return min_deps


def create_zip_file(zip_dir, env_yml=None, min_deps=None, quiet=False):
    """Create a zip file of a directory

    Args:
        :zip_dir: The directory to zip

    Kwargs:
        :env_yml=None (str): If provided, the string is copied as the
            ``env.yml`` file in the zip archive
        :min_deps=None (str): If provided, the string is copied as the
            ``min-deps.json`` file in the zip archive
        :quiet=False: If True, no messages are printed

    Return:
        A bytes buffer containing the zip file data
    """
    buf = BytesIO()
    zip_file = zipfile.ZipFile(buf, 'w')
    if env_yml:
        with open('env.yml', 'w') as f_obj:
            f_obj.write(env_yml)
        zip_file.write('env.yml')
        os.unlink('env.yml')
    if min_deps:
        with open('min-deps.json', 'w') as f_obj:
            f_obj.write(json.dumps(min_deps))
        zip_file.write('min-deps.json')
        os.unlink('min-deps.json')
    zip_file.write(zip_dir)
    for pardir, _, files in os.walk(zip_dir):
        for filename in files:
            if not quiet:
                print('Zipping %s' % os.path.join(pardir, filename))
            zip_file.write(os.path.join(pardir, filename))
    zip_file.close()
    return buf.getvalue()


def send_data(app_name, path, data, name, quiet=False):
    """Send data back to the server

    Args:
        :app_name (str): The name of the application
        :path (str): The path to send data to, without the base address
        :data: Buffer containing the data
        :name (str): The name to use for the data in messages

    Kwargs:
        :quiet=False (bool): If True, no messages are printed
    """
    if sys.version_info[0] == 2:
        __data = base64.urlsafe_b64encode(data)
    else:
        __data = base64.urlsafe_b64encode(data).decode('utf-8')

    data_json = json.dumps({'name': app_name, 'data': __data}).encode('utf-8')
    req = Request('http://%s:%d/%s' % (HOST, PORT, path),
                  data=data_json)
    resp = urlopen(req)
    resp.read()

    if not quiet:
        if resp.getcode() == 200:
            print('%s sent succesfully' % name)
        else:
            print('Error while sending %s' % name)
            print('Response code is %d' % resp.status)


def send_env_yml(app_name, env_yml, quiet=False):
    """Send the environment yml data back to the server

    Args:
        :app_name (str): The name of the application
        :env_yml: Buffer containing the environment yml data

    Kwargs:
        :quiet=False (bool): If True, no messages are printed
    """
    return send_data(app_name, 'yml', env_yml.encode('utf-8'), 'Environment yml file', quiet=quiet)


def send_repo_zip(app_name, zip_file, quiet=False):
    """Send a zip of the repository back to the server

    Args:
        :app_name (str): The name of the application
        :zip_file: Buffer containing the zip of the code repository

    Kwargs:
        :quiet=False (bool): If True, no messages are printed
    """
    return send_data(app_name, 'zip', zip_file, 'Package zip file', quiet=quiet)


def send_min_deps(app_name, min_deps, quiet=False):
    """Send a zip of the repository back to the server

    Args:
        :app_name (str): The name of the application
        :min_deps (list): List containing the minimal required dependencies

    Kwargs:
        :quiet=False (bool): If True, no messages are printed
    """
    return send_data(app_name, 'min', json.dumps(min_deps).encode('utf-8'),
                     'Minimal dependency list', quiet=quiet)


def main(cl_args=None, save_zip=None):
    """Main function that is executed

    Kwargs:
        :cl_args=None (argparse.Namespace): Any command line args that have
            been parsed.
        :save_zip=None (bool): If True, a zip file is created for saving
            without prompting the user. Otherwise, the user is prompted for
            the action.
    """
    if sys.version_info[0] == 2:
        input = raw_input
    else:
        input = __builtins__['input']

    if cl_args is None and len(sys.argv) > 1:
        cl_args = parse_args()

    print('Attempting to identify conda environment and packages')
    success, env_yml, err = get_conda_env()

    if success:
        env = env_yml.split('\n')[0].split(':')[1].strip()
        print('Using environment %s' % env)
        source_env = False
    else:
        print('Failed to identify environment')
        env = input('Which conda environment should be activated: ').strip('\n')
        success, env_yml, err = get_conda_env(env)
        if not success:
            sys.stderr.write('Failed to collect conda environment details\n')
            # Python 2 compatibilty requires the str(err.decode(...))
            # In Python 3, it will cast str to str and in Python it will cast unicode to str
            # Either ways, it will create the proper string for printing out
            sys.stderr.write('Error is:\n%s' % str(err.encode('utf-8')))
            sys.stderr.write('Please activate manually and rerun\n')
            sys.exit(-1)
        source_env = True

    print('Trying to create a minimal dependency list...this may take some time')
    min_deps = get_conda_min_deps(env, source_env=source_env)
    if min_deps is None or min_deps == []:
        print('Failed to obtain minimal dependencies...continuing with all packages')

    if cl_args is not None and cl_args.name is not None:
        app_name = cl_args.name
    else:
        app_name = input('Please enter name of application: ')

    if cl_args is not None and cl_args.dir is not None:
        zip_dir = cl_args.dir
    else:
        zip_dir = input('Please enter the directory of the source code to zip: ')

    if save_zip or (cl_args is not None and cl_args.zip):
        __save_zip = 'y'
    elif cl_args is not None:
        __save_zip = 'n'
    else:
        __save_zip = input('Do you want to save the zip file for emailing later? (y/n): ')
        while __save_zip not in ('y', 'n'):
            __save_zip = input('Please enter y or n: ')

    os.chdir(os.path.abspath(zip_dir) + os.path.sep + os.path.pardir)
    if __save_zip == 'y':
        if min_deps:
            zip_file = create_zip_file(os.path.relpath(zip_dir),
                                       env_yml, min_deps)
        else:
            zip_file = create_zip_file(os.path.relpath(zip_dir), env_yml)
        print('Saving zip file as %s.zip' % app_name)
        with open('%s.zip' % app_name, 'w+b') as zip_file_obj:
            zip_file_obj.write(zip_file)
    else:
        zip_file = create_zip_file(os.path.relpath(zip_dir))
        send_env_yml(app_name, env_yml)
        send_repo_zip(app_name, zip_file)
        if min_deps:
            send_min_deps(app_name, min_deps)
        print('All data has been copied to target system.')
        print('You can now attempt setting up the software there')


if __name__ == '__main__':
    main()
