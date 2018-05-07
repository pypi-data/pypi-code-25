import urllib.request
import base64
import os
import sys
import subprocess
import json

from . import utils
from . import env
from . import utils

BITBUCKET_SSH_PATH = "/opt/atlassian/pipelines/agent/data/id_rsa"


def build(deployment_info, **kwargs):
    print(utils.color_string(utils.BUILD_TITLE,
                             utils.GREEN_COLOR, utils.DEFAULT_COLOR))

    if not deployment_info.is_deploy:
        print('INGORE BUILD!')
        return

    print('\nBuild docker image')
    res = subprocess.run('docker build --build-arg SSH_PRIVATE_KEY="$(cat {ssh_path})" --build-arg GIT_COMMIT={git_commit} --build-arg SERVICE_VERSION={service_version} --build-arg BUILD_NUMBER={build_number} -t {image_name}:{image_tag} .'.format(
        image_name=env.FOSSILCI_DOCKER_IMAGE, image_tag=deployment_info.image_tag, ssh_path=BITBUCKET_SSH_PATH, service_version=deployment_info.service_version, git_commit=env.GIT_COMMIT, build_number=env.BITBUCKET_BUILD_NUMBER), shell=True)
    if res.returncode != 0:
        raise subprocess.CalledProcessError(res.returncode, res.args)

    print('\nPush docker image to ECR')
    res = subprocess.run('docker push {image_name}:{image_tag}'.format(
        image_name=env.FOSSILCI_DOCKER_IMAGE, image_tag=deployment_info.image_tag), shell=True)
    if res.returncode != 0:
        raise subprocess.CalledProcessError(res.returncode, res.args)


def test(deployment_info, **kwargs):
    pass


def deploy(deployment_info):
    print(utils.color_string(utils.DEPLOY_TITLE,
                             utils.GREEN_COLOR, utils.DEFAULT_COLOR))

    if not deployment_info.is_deploy:
        print('INGORE DEPLOY!')
        return

    if deployment_info.unsupported_brands:
        print(utils.color_string('Unsupported brands for deployment:',
                                 utils.MAGENTA_COLOR, utils.DEFAULT_COLOR))
        for brand in deployment_info.unsupported_brands.items():
            print('\t*{b}'.format(b=brand))

    for brand, services in deployment_info.services.items():
        print('\tDeploy for brand: "{bc1}{b}{bc2}"'.format(
            bc1=utils.GREEN_COLOR, b=brand, bc2=utils.DEFAULT_COLOR))

        for service in services:
            print('\tStart deploy for service : "{sc1}{s}{sc2}"'.format(
                sc1=utils.GREEN_COLOR, s=service, sc2=utils.DEFAULT_COLOR))

            trigger_jenkins(env.JENKINS_URL, env.JENKINS_USER, env.JENKINS_USER_TOKEN,
                            service, env.JENKINS_JOB_TOKEN, deployment_info.image_tag)

        print('\n\n')


def generate_doc(**kwargs):
    print(utils.color_string("Generating API documents",
                             utils.GREEN_COLOR, utils.DEFAULT_COLOR))
    if kwargs['language'] == 'go':
        package_path = "{go_path}/src/bitbucket.org/{bitbucket_repo_owner}/{bitbucket_repo_slug}".format(
            go_path=os.environ["GOPATH"], bitbucket_repo_owner=os.environ[
                "BITBUCKET_REPO_OWNER"], bitbucket_repo_slug=env.BITBUCKET_REPO_SLUG
        )
        subprocess.check_output(
            'mkdir -pv "{p}"'.format(p=package_path), shell=True)
        subprocess.check_output(
            'tar -cO --exclude=bitbucket-pipelines.yml . | tar -xv -C "{p}"'.format(p=package_path), shell=True)

        cwd = os.getcwd()
        os.chdir(package_path)
        subprocess.run("dep ensure -v -vendor-only", shell=True)
        os.chdir(package_path + "/api")
        subprocess.run(
            "swagger generate spec --scan-models -o {file}".format(file=kwargs['out']), shell=True)
        subprocess.run(
            "mv {file} {dest}".format(file=kwargs['out'], dest=cwd), shell=True)

        os.chdir(cwd)

    print("Done")


def push_doc(**kwargs):
    print(utils.color_string("Pushing API documents",
                             utils.GREEN_COLOR, utils.DEFAULT_COLOR))
    url = kwargs['url']
    if not url:
        url = env.FOSSILCI_DOC_URL

    key = kwargs['key']
    if not key:
        key = env.FOSSILCI_DOC_KEY

    doc_env = kwargs['env']
    if not doc_env:
        if env.FOSSILCI_DEPLOY_ENV == 'dev' or env.FOSSILCI_DEPLOY_ENV == 'development':
            doc_env = 'dev'
        else:
            doc_env = 'default'

    ver = kwargs['version']
    if not ver:
        ver = env.FOSSILCI_DOC_VERSION

    project = kwargs['project']
    if not key:
        project = env.FOSSILCI_DOC_PROJECT

    with open(kwargs['file'], 'r') as doc_file:
        data = doc_file.read()

    body = {
        'env': doc_env,
        'project': project,
        'service': env.BITBUCKET_REPO_SLUG,
        'version': ver,
        'data': data,
    }

    params = json.dumps(body).encode('utf8')
    request = urllib.request.Request(url, data=params, headers={
                                     'content-type': 'application/json'})
    request.add_header("API-Master-Key", key)

    urllib.request.urlopen(request)

    print("Done")


def trigger_jenkins(jenkins_url, jenkins_user, jenkins_user_token, job_name, job_token, image_tag):
    """
    Trigger deploy job on Jenkins.
    """
    url = '{jenkins_url}/job/{job_name}/buildWithParameters?token={job_token}&_IMAGE_TAG={image_tag}&cause=Bitbucket+pipeline+trigger'.format(
        jenkins_url=jenkins_url, job_name=job_name, job_token=job_token, image_tag=image_tag)
    request = urllib.request.Request(url)

    basic_auth = base64.standard_b64encode("{user}:{token}".format(
        user=jenkins_user, token=jenkins_user_token).encode('utf-8'))

    request.add_header(
        "Authorization", "Basic %s" % basic_auth.decode('utf-8'))

    urllib.request.urlopen(request)
