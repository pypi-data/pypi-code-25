from __future__ import absolute_import
import os

USE_GPU = False

DOCKER_IMAGE = u"dementrock/rllab23-shared"

KUBE_PREFIX = u"template_"

DOCKER_LOG_DIR = u"/tmp/expt"

AWS_IMAGE_ID = u"ami-67c5d00d"

if USE_GPU:
    AWS_INSTANCE_TYPE = u"g2.2xlarge"
else:
    AWS_INSTANCE_TYPE = u"c4.2xlarge"

AWS_KEY_NAME = u"research_virginia"

AWS_SPOT = True

AWS_SPOT_PRICE = u'10.0'

AWS_IAM_INSTANCE_PROFILE_NAME = u"rllab2"

AWS_SECURITY_GROUPS = [u"rllab2"]

AWS_REGION_NAME = u"us-west-2"

AWS_CODE_SYNC_S3_PATH = u"<insert aws s3 bucket url for code>e"

CODE_SYNC_IGNORES = [u"*.git/*", u"*data/*", u"*src/*",
                     u"*.pods/*", u"*tests/*", u"*examples/*", u"docs/*"]

LOCAL_CODE_DIR = u"<insert local code dir>"

AWS_S3_PATH = u"<insert aws s3 bucket url>"

LABEL = u"template"

DOCKER_CODE_DIR = u"/root/code/rllab2"

AWS_ACCESS_KEY = os.environ.get(u"AWS_ACCESS_KEY", u"<insert aws key>")

AWS_ACCESS_SECRET = os.environ.get(u"AWS_ACCESS_SECRET", u"<insert aws secret>")
