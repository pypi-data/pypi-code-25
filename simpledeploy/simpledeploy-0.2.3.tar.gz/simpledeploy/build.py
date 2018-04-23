import docker
import simpledeploy.dockerfile

def main(args):
    createDockerfile()

def createDockerfile(sourceImage='scratch'):
    with open('Dockerfile.simpledeploy', 'w+') as file:
        file.write(dockerfile.dockerFrom(sourceImage))
        file.write(dockerfile.appDirectory())
        file.seek(0)
        print(file.read())
