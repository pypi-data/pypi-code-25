from pathlib import Path
from subprocess import *
from tempfile import *
import re, platform, os, json, sys, argparse, signal, urllib, tarfile, tempfile

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='a subcommand')
    init_parser = subparsers.add_parser('init', help='initialize ipfs and add the save hook to the jupyter config file')
    init_parser.set_defaults(func=init)
    launch_parser = subparsers.add_parser('launch', help='create an environment for and launch a jupyter notebook')
    launch_parser.set_defaults(func=launch)
    start_parser = subparsers.add_parser('start', help='starts the upload daemon')
    start_parser.set_defaults(func=start)
    stop_parser = subparsers.add_parser('stop', help='stops the upload daemon')
    stop_parser.set_defaults(func=stop)
    launch_parser.add_argument('notebook', metavar='NOTEBOOK', type=str, nargs=1, help='an integer for the accumulator')
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        parsed = parser.parse_args()
        parsed.func(parsed)
        
def start(parsed_args):
    pid = os.fork()
    if pid == 0:
        os.execl(ipfs(), "ipfs", "daemon")
    else:
        with open(Path(gettempdir()) / "nyptune.pid", "w") as file:
            file.write(str(pid)+"\n")

def stop(parsed_args):
    pid_path = Path(gettempdir()) / "nyptune.pid"
    if pid_path.is_file():
        with open(pid_path) as file:
            pid = file.read()
            os.kill(int(pid), signal.SIGTERM)
            pid_path.unlink()
    else:
        print("Nyptune daemon not running: no pid file found")

def ipfs():
    return str(Path(os.path.realpath(__file__)).parent / 'go-ipfs' / 'ipfs')
        
def launch(parsed_args):
    notebook = parsed_args.notebook[0]
    cache = Path(notebook).parent / '.cache'
    with open(notebook) as file:
        model = json.load(file)
        conda = '\n'.join([line for line in model['metadata']['magix']['conda'] if line != '@EXPLICIT'])
        with NamedTemporaryFile() as conda_env_yaml:
            conda_env_yaml.write(conda.encode('utf-8'))
            conda_env_yaml.flush()
            print(conda_env_yaml.name)
            result = run(['conda', 'create', '-y', '--name', sys.argv[1], '--file', conda_env_yaml.name], encoding = 'utf-8', shell = False)
            if result.returncode != 0:
                result = run(['conda', 'env', 'update', '-y', '--name', sys.argv[1], '--file', conda_env_yaml.name], encoding = 'utf-8', shell = False)
        sig = model['metadata']['magix']['cache']['.cache']
        run([ipfs(), 'get', sig, '-o', cache], shell = False)
        with NamedTemporaryFile() as requirements:
            pip = '\n'.join(model['metadata']['magix']['pip'])
            requirements.write(pip.encode('utf-8'))
            requirements.flush()
            with NamedTemporaryFile() as script:
                s = [
                    '#!/bin/bash',
                    'source activate '+sys.argv[1],
                    'pip install -y -r '+requirements.name,
                    'jupyter notebook'
                ]
                script.write('\n'.join(s).encode('utf-8'))
                script.flush()
                os.chmod(script.name, 0o755)
                print('running '+script.name)
                print('\n'.join(s))
                os.execl(script.name, 'jupyter')
                
                # #!/bin/bash
                # cd `dirname $0`
                #
                # version=0.4.14
                #
                # for platform in darwin linux
                # do
                #     for arch in 386 amd64
                #     do
                #         wget https://dist.ipfs.io/go-ipfs/v${version}/go-ipfs_v${version}_${platform}-${arch}.tar.gz
                #         tar -zxvf go-ipfs_v${version}_${platform}-${arch}.tar.gz
                #         mkdir -p nyptune/ipfs/${platform}-${arch}
                #         cp go-ipfs/ipfs nyptune/ipfs/${platform}-${arch}/
                #         rm -rf go-ipfs
                #         rm go-ipfs_v${version}_${platform}-${arch}.tar.gz
                #     done
                # done
                #
    
        
def init(parsed_args):
    config = Path.home() / '.jupyter' / 'jupyter_notebook_config.py'
    if not config.is_file():
        print('generating an empty jupyter config file')
        run(['jupyter', 'notebook', '--generate-config'], encoding = 'utf-8', shell = False)
    with open(config, 'r') as file:
        contents = file.read()
        
    if 'nyptune' in contents:
        print('jupyter config file already mentions nyptune')
    else:
        with open(config, 'a') as file:
            print('appending nyptune pre-save-hook to jupyter config')
            file.write('\nfrom nyptune.jupyter import presave\nc.ContentsManager.pre_save_hook = presave\n')
            
    if '64' in platform.machine():
        arch = 'amd64'
    else:
        arch = '386'
    plat = platform.system().lower()
    version='0.4.14'
    local = Path(tempfile.gettempdir()) / "go-ipfs.tar.gz"
    urllib.request.urlretrieve(f"https://dist.ipfs.io/go-ipfs/v{version}/go-ipfs_v{version}_{plat}-{arch}.tar.gz", local)
    with tarfile.open(local, 'r|gz') as tar:
        tar.extractall(Path(os.path.realpath(__file__)).parent)
    print('initializing ipfs')
    run([ipfs(), 'init'], encoding = 'utf-8', shell = False)
    run([ipfs(), 'config', '--json', 'Experimental.FilestoreEnabled', 'true'], encoding = 'utf-8', shell = False)