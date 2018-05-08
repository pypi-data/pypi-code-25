import subprocess

def run_in_foreground(cmd):
    print(cmd)
    return subprocess.check_output(cmd.split(), shell=False)
