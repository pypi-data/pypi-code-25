from requests.exceptions import ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout
from os.path import basename
from path import Path
import traceback
import datetime
import tempfile
import requests
import logging
import zipfile
import yaml
import glob
import json
import os
from os import getenv
import pika
import time


logger = logging.getLogger('{}'.format(
        __name__
    ))
def _load_yaml(conf_file_name_path):
    with open(conf_file_name_path, 'r') as stream:
        try:
            _settings = yaml.load(stream)
        except yaml.YAMLError as exc:
            logger.error('error loading %s yaml file', conf_file_name_path)
    return _settings

def rmtree(dir):
    if Path(dir).exists():
        Path(dir).rmtree_p()
        logger.info('removed dir : %s ', dir)


def _tempdir(dir=None):
    d = tempfile.mkdtemp(dir=dir)
    return Path(d)

def write_to_zipfile(master_zipfilename, output_dir, files_dir, type):
    """This function will create the final zip file for all subscriptions """
    output_file = ''
    master_zipfile = output_dir / master_zipfilename
    try:
        with zipfile.ZipFile(master_zipfile, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            pass
        p = files_dir
        logger.info('creating zip file of all %s data', type)
        with zipfile.ZipFile(master_zipfile, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for f in p.walkfiles():
                if basename(f).startswith("merged"):
                    zf.write(f, f.relpath(p))
                    logger.debug('file to zip : %s',f.relpath(p))
        output_file =  zf.filename
    except Exception as e:
        logger.error('error in zipping %s csv files', type)
        logger.error(traceback.format_exc())
    return output_file

def write_to_account_zipfile(zipfilename, prefix, account, output_dir, files_dir, type):
    """This function will create the zip file for type supplied """
    output_file = ''
    zipabsfilename = output_dir / zipfilename   # absolute name of zip file
    try:
        with zipfile.ZipFile(zipabsfilename, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            pass
        p = files_dir
        logger.info('creating zip file of %s data', type)
        with zipfile.ZipFile(zipabsfilename, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for f in p.walkfiles():
                if basename(f).startswith(prefix + '_' + account):  # This should be one file only
                    zf.write(f, f.relpath(p))
                    logger.debug('file to zip : %s',f.relpath(p))
        output_file = zf.filename
    except Exception as e:
        logger.error('error in zipping %s csv files', type)
        logger.error(traceback.format_exc())
    return output_file

def compress(outputzip, filetozip):
    output_file = ''
    try:
        with zipfile.ZipFile(outputzip, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            pass
        with zipfile.ZipFile(outputzip, 'a', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            zf.write(filetozip, basename(filetozip))
        output_file =  zf.filename
    except Exception as e:
        logger.error('error in compressing file %s', filetozip)
        logger.error(traceback.format_exc())
    return output_file

def now(dateformat):
    return datetime.datetime.now().strftime(dateformat)

def load(confdir=None):
    confdir = find_basedir() + os.sep + 'conf'
    f=glob.glob(confdir + os.sep + '01-default.yaml')
    y = {}
    with open(f[0], 'r') as stream:
        try:
            y = yaml.load(stream)   # Assuming only one file 01-Default.yaml is returned by glob
        except Exception as e:
            traceback.print_exc()
    return y

def reply_body(_type, billing_account_number, asset_account_number, _status, _period, _response_code, _response, _filepath):
    body = {"type":"", "billing_acount_number":"", "asset_account_number":"","status":"", "period":"", "response_code":"", "response":"", "filepath":""}
    body['type'] = _type
    body['billing_acount_number'] = billing_account_number
    body['asset_account_number'] = asset_account_number
    body['status'] = _status
    body['period'] = _period
    body['response_code'] = _response_code
    body['response'] = _response
    body['filepath'] = _filepath
    return json.dumps(body);

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def find_basedir():

    p = os.environ.get('CAMDATA_BASEDIR')
    if p:
        return Path(p)

    # TODO: come up with a better way to do this
    # This function is copied from cam-extractor. Another method is to recursively traverse directory path backwards
    # and find for packages directory, finding conf is then easy.
    #   this is horribly ugly...

    for basedir in (
            '.',
            '..',
            '../..',
            '../../..',
            '../../../..',
            '../../../../..',
            '../../../../../..',
            '../../../../../../..',
            '../../../../../../../..',
            '/opt/camdata', # current hard-coded path in docker camdata-ingestor
            '/usr/work', # current hard-coded path in docker camdata-server
            ):
        p = Path(basedir).abspath()
        if (p / 'conf/01-default.yaml').exists():
            return p
        if (p / 'conf/01-default.yml').exists():
            return p

    return Path('.').abspath()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def retry(exception_to_check, tries=8, delay=1, backoff=2, logger=None):
    from functools import wraps
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_to_check, e:
                    logger.warning("%s, Retrying in %d seconds..." % (str(e), mdelay))
                    import time
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry

    return deco_retry
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def process_message(message):

    # create a dictionary and put all values in that
    mdict = {}
    mdict['months'] = int(message['months'])
    count=0
    l2=[]
    daccount = {'billing_account_number': '', 'vserver': '', 'username':'','password':'',
                'tenant':'','months': '', 'asset_accounts': ''}
    for account in message['accounts']:
        daccount['billing_account_number'] = account['billing_account_number']
        daccount['vserver'] = account['credentials']['vserver']
        daccount['username'] = account['credentials']['username']
        daccount['password'] = account['credentials']['password']
        if 'tenant' in account['credentials']:
            daccount['tenant'] = account['credentials']['tenant']
        daccount['months'] = account['months']
        cnt = 0
        l1 = []
        # Taking all values in a dictionary which will be required for regenerating expired token
        dasset = {'asset_account_number': '', 'api_key': '', 'vserver':'', 'username':'','password':'','tenant':''}
        for acct in account['asset_accounts']:
            if not acct['asset_account_number']:
                logger.info('there is no vRA integrated with this vCenter account, asset account number will be named as default-asset-account')
                dasset['asset_account_number'] = 'default-asset-account'
                l1.append(dasset.copy())
            else:
                dasset['asset_account_number'] = acct['asset_account_number']
                dasset['vserver'] = acct['credentials']['vserver']
                dasset['username'] = acct['credentials']['username']
                dasset['password'] = acct['credentials']['password']
                if 'tenant' in acct['credentials']:
                    dasset['tenant'] = acct['credentials']['tenant']
                    logger.info('getting token id for tenant %s', dasset['tenant'])
                    print 'dasset', dasset
                    try:
                        dasset['api_key'] = get_vmware_token(dasset.copy())
                    except Exception as e:
                        logger.error('failed to get vmware token id, this will affect asset and utilization extraction')
                l1.append(dasset.copy())
        daccount['asset_accounts'] = l1
        l2.append(daccount.copy())
    mdict['accounts'] = l2

    return mdict


def create_connection():
    _config = load()
    broker_config = _config['vmware']['broker']
    host = getenv('BROKER_HOST')
    port = getenv('BROKER_PORT')
    logger.info('port = %s host = %s', port, host)
    if not host:
        raise EnvironmentError('Environment variable BROKER_HOST is not defined')
    if not port:
        raise EnvironmentError('Environment variable BROKER_PORT is not defined')
    queue = broker_config['queue']
    username = getenv('BROKER_USERNAME')
    password = getenv('BROKER_PASSWORD')
    params_kwargs = {}
    if username and password:
        credentials = pika.PlainCredentials(username, password)
        params_kwargs['credentials'] = credentials
    # consume messages from request queue
    params = pika.ConnectionParameters(host=host, port=int(port), heartbeat_interval=600,
        **params_kwargs)
    # This is a temporary fix to stop pika from crashing everytime a connection fails
    # This will be removed once we move to Kombu
    total_wait_time = 120  # seconds
    sleep_time = 5  # seconds
    timeout = 0
    while True:  # keep trying the connection for 120 seconds
        try:
            connection = pika.BlockingConnection(params)
            break
        except Exception as e:
            logger.warn('Error occurred, trying to reconnect now  %s', e)
            if timeout < total_wait_time:
                time.sleep(sleep_time)
                timeout = timeout + sleep_time
            else:
                logger.error('Unable to reconnect after %s seconds . The following error occurred %s ', total_wait_time,
                             e)
                raise e
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    logger.info('connection creation successful with port = %s host = %s', port, host)
    return channel

@retry((ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout), tries=8, delay=1, backoff=2
                 , logger=logger)
def get_vmware_token(account):
    api_url = 'https://{}/identity/api/tokens'.format(account['vserver'])
    payload = {'username': '{}'.format(account['username']), 'password': '{}'.format(account['password']),
               'tenant': '{}'.format(account['tenant'])}
    response = requests.post(api_url, json=payload, verify=False)
    return response.json()['id']
