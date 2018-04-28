from __future__ import absolute_import
import os.path as osp
import os

PROJECT_PATH = osp.abspath(osp.join(osp.dirname(__file__), u'..'))

LOG_DIR = PROJECT_PATH + u"/data"

USE_TF = False

DOCKER_IMAGE = u"DOCKER_IMAGE"

DOCKERFILE_PATH = u"/path/to/Dockerfile"

KUBE_PREFIX = u"rllab2_"

DOCKER_LOG_DIR = u"/tmp/expt"

POD_DIR = PROJECT_PATH + u"/.pods"

AWS_S3_PATH = None

AWS_IMAGE_ID = None

AWS_INSTANCE_TYPE = u"m4.xlarge"

AWS_KEY_NAME = u"AWS_KEY_NAME"

AWS_SPOT = True

AWS_SPOT_PRICE = u'1.0'

AWS_ACCESS_KEY = os.environ.get(u"AWS_ACCESS_KEY", None)

AWS_ACCESS_SECRET = os.environ.get(u"AWS_ACCESS_SECRET", None)

AWS_IAM_INSTANCE_PROFILE_NAME = u"rllab2"

AWS_SECURITY_GROUPS = [u"rllab2"]

AWS_SECURITY_GROUP_IDS = []

AWS_NETWORK_INTERFACES = []

AWS_EXTRA_CONFIGS = dict()

AWS_REGION_NAME = u"us-east-1"

CODE_SYNC_IGNORES = [u"*.git/*", u"*data/*", u"*.pod/*"]

DOCKER_CODE_DIR = u"/root/code/rllab2"

AWS_CODE_SYNC_S3_PATH = u"s3://to/be/overriden/in/personal"

# whether to use fast code sync
FAST_CODE_SYNC = True

FAST_CODE_SYNC_IGNORES = [u".git", u"data", u".pods"]

KUBE_DEFAULT_RESOURCES = {
    u"requests": {
        u"cpu": 0.8,
    }
}

KUBE_DEFAULT_NODE_SELECTOR = {
    u"aws/type": u"m4.xlarge",
}

MUJOCO_KEY_PATH = osp.expanduser(u"~/.mujoco")
# MUJOCO_KEY_PATH = osp.join(osp.dirname(__file__), "../vendor/mujoco")

ENV = {}

EBS_OPTIMIZED = True

if osp.exists(osp.join(osp.dirname(__file__), u"config_personal.py")):
    from .config_personal import *
else:
    print u"Creating your personal config from template..."
    from shutil import copy
    copy(osp.join(PROJECT_PATH, u"rllab2/config_personal_template.py"), osp.join(PROJECT_PATH, u"rllab2/config_personal.py"))
    from .config_personal import *
    print u"Personal config created, but you should probably edit it before further experiments " \
          u"are run"
    if u'CIRCLECI' not in os.environ:
        print u"Exiting."
        import sys; sys.exit(0)

LABEL = u""
