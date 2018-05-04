"""
Environment example:
    FOSSILCI_DEPLOY_ENV             "prd" or "stg"
    FOSSILCI_DOCKER_IMAGE           "315962882822.dkr.ecr.us-east-1.amazonaws.com/k8s-portfolio-microservices"
    FOSSILCI_BRANDS                 "fossil;skagen;mk"
    FOSSILCI_JOBS                   "as-v2-api;as-v2-consumer;as-v2-scheduler"
    FOSSILCI_JOBS_NAME_MAPPINGS     "skagen-as-v2-api=skagen-as"
"""
import os


def dict_array_environ(key):
    '''
    Parse value from an environment variable to a dict of array.
    The value of environment variable must be in format:
        ENV_VAR="key1=val1.1,val1.2;key2=val2.1,val2.2"
    '''
    dict_env = {}
    value = os.environ.get(key, default="")
    pairs = [x.strip() for x in value.split(';') if x.strip()]
    for pair in pairs:
        key_value = pair.strip().split('=')
        dict_env[key_value[0].strip()] = [x.strip()
                                          for x in key_value[1].split(',') if x.strip()]

    return dict_env


def dict_environ(key):
    '''
    Parse value from an environment variable to a dict.
    The value of environment variable must be in format:
        ENV_VAR="key1=val1;key2=val2"
    '''
    dict_env = {}
    value = os.environ.get(key, default="")
    pairs = [x.strip() for x in value.split(';') if x.strip()]
    for pair in pairs:
        key_value = pair.strip().split('=')
        dict_env[key_value[0].strip()] = key_value[1].strip()

    return dict_env


def array_environ(key):
    '''
    Parse value from an environment variable to a array.
    The value of environment variable must be in format:
        ENV_VAR="elem1;elem2"
    '''
    return [x.strip() for x in os.environ.get(key, default="").split(';') if x.strip()]


'''
FossilCI environment variables.
'''
FOSSILCI_DEPLOY_ENV = os.environ['FOSSILCI_DEPLOY_ENV']
FOSSILCI_DOCKER_IMAGE = os.environ['FOSSILCI_DOCKER_IMAGE_{env}'.format(
    env=FOSSILCI_DEPLOY_ENV.upper())]
FOSSILCI_BRANDS = array_environ('FOSSILCI_BRANDS')
FOSSILCI_JOBS = array_environ('FOSSILCI_JOBS')
FOSSILCI_JOBS_NAME_MAPPINGS = dict_environ('FOSSILCI_JOBS_NAME_MAPPINGS')
FOSSILCI_BRANCHES_BRANDS = dict_array_environ('FOSSILCI_BRANCHES_BRANDS')

FOSSILCI_DOC_URL = os.environ.get('FOSSILCI_DOC_URL', '')
FOSSILCI_DOC_VERSION = os.environ.get('FOSSILCI_DOC_VERSION', '')
FOSSILCI_DOC_KEY = os.environ.get('FOSSILCI_DOC_KEY', '')
FOSSILCI_DOC_PROJECT = os.environ.get('FOSSILCI_DOC_PROJECT', '')

'''
Bitbucket environment variables.
'''
GIT_COMMIT = os.environ["BITBUCKET_COMMIT"]
GIT_BRANCH = os.environ.get("BITBUCKET_BRANCH", default="")
GIT_TAG = os.environ.get("BITBUCKET_TAG", default="")
BITBUCKET_REPO_SLUG = os.environ["BITBUCKET_REPO_SLUG"]
BITBUCKET_BUILD_NUMBER = os.environ["BITBUCKET_BUILD_NUMBER"]

'''
Jenkins environment variables.
'''
JENKINS_JOB_TOKEN = os.environ["JENKINS_JOB_TOKEN_{env}".format(
    env=FOSSILCI_DEPLOY_ENV.upper())]
JENKINS_USER_TOKEN = os.environ["JENKINS_USER_TOKEN_{env}".format(
    env=FOSSILCI_DEPLOY_ENV.upper())]
JENKINS_USER = os.environ["JENKINS_USER_{env}".format(
    env=FOSSILCI_DEPLOY_ENV.upper())]
JENKINS_URL = os.environ["JENKINS_URL_{env}".format(
    env=FOSSILCI_DEPLOY_ENV.upper())]

'''
AWS environment variables.
'''
AWS_ACCESS_KEY_ID = os.environ[
    "AWS_ACCESS_KEY_ID_{env}".format(env=FOSSILCI_DEPLOY_ENV.upper())]
AWS_SECRET_ACCESS_KEY = os.environ[
    "AWS_SECRET_ACCESS_KEY_{env}".format(env=FOSSILCI_DEPLOY_ENV.upper())]
AWS_DEFAULT_REGION = os.environ[
    "AWS_DEFAULT_REGION_{env}".format(env=FOSSILCI_DEPLOY_ENV.upper())]

os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
os.environ["AWS_DEFAULT_REGION"] = AWS_DEFAULT_REGION
