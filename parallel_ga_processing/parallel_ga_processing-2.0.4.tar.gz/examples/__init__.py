from parallel_ga_processing.algorithmRunners import launch
import os

if __name__ == '__main__':
    path = str(os.getcwd()) + "/"
    executable = "try.py"
    launch(["localhost", "remote1@remote1-VirtualBox"], 36, path, executable)
