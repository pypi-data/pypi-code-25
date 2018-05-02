from threading import Thread

from docker import from_env

from src.config import ROOT_DIR


def write_docker_log():
    client = from_env()
    for container in client.containers.list():
        for line in container.logs(stream=True):
            with open('%s/result/%s.log' % (ROOT_DIR, container.attrs['Id']), 'a') as f:
                f.writelines(line)


class ContainerLog:
    def __init__(self):
        job = Thread(target=write_docker_log())
        job.start()
