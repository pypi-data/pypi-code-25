import urllib.request
import base64
import os
import sys
import subprocess

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
    res = subprocess.run('docker build --build-arg SSH_PRIVATE_KEY="$(cat {ssh_path})" -t {image_name}:{image_tag} .'.format(
        image_name=env.FOSSILCI_DOCKER_IMAGE, image_tag=deployment_info.image_tag, ssh_path=BITBUCKET_SSH_PATH), shell=True)
    if res.returncode != 0:
        raise subprocess.CalledProcessError(res.returncode, res.args)

    print('\nPush docker image to ECR')
    subprocess.run('docker push {image_name}:{image_tag}'.format(
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
        try:
            print('\tDeploy for brand: "{bc1}{b}{bc2}"'.format(
                bc1=utils.GREEN_COLOR, b=brand['name'], bc2=utils.DEFAULT_COLOR))

            for service in services:
                print('\tStart deploy for service : "{sc1}{s}{sc2}"'.format(
                    sc1=utils.GREEN_COLOR, s=service, sc2=utils.DEFAULT_COLOR))

                trigger_jenkins(env.JENKINS_URL, env.JENKINS_USER, env.JENKINS_USER_TOKEN, "{env}-{service}".format(
                    env=env.FOSSILCI_DEPLOY_ENV, service=service), env.JENKINS_JOB_TOKEN, deployment_info.image_tag)

            print('\n\n')

        except:
            typ, value, tb = sys.exc_info()
            utils.my_except_hook(typ, value, tb)


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
