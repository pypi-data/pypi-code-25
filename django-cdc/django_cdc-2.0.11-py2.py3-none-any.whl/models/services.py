import json
import logging
from datetime import datetime, time

from botocore.exceptions import ClientError
from django.db.models.fields.files import ImageFieldFile
from decimal import Decimal

from constants import ServiceType
from django_cdc import settings
from . import lambda_client, kinesis_client, sns_client, sns_arn, \
    kafka_producer_client
import uuid
import hashlib
from django_cdc.settings import SNS_TOPIC_NOT_EXIST_MESSAGE, SNS_NOTFOUND_CODE

logger = logging.getLogger(__name__)

try:
    from django.utils.timezone import now as datetime_now
    from bitfield.types import BitHandler
    assert datetime_now
    assert BitHandler
except ImportError:
    from datetime import datetime
    BitHandler = object.__class__
    datetime_now = datetime.now


class Service(object):
    def factory(type):
        if type == ServiceType.KINESIS:
            return kinesis_service()
        elif type == ServiceType.SNS:
            return SNS_service()
        elif type == ServiceType.LAMBDA_KINESIS:
            return lambda_service()
        elif type == ServiceType.ASYNC_KAFKA_PRODUCER:
            return AsyncKafka_Service()
        elif type == ServiceType.SYNC_KAFKA_PRODUCER:
            return SyncKafka_Service()
        else:
            return
        assert 0, "Bad Service Request: " + type

    factory = staticmethod(factory)


class PythonObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ImageFieldFile) or isinstance(obj, datetime) \
                or isinstance(obj, time) or isinstance(obj, BitHandler)\
                or isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class CommonUtils(object):
    def get_function_name(self, table_name, service_custom_name=None):
        if service_custom_name:
            function_name = service_custom_name
        else:
            function_name = "{0}{1}{2}".format(
                settings.SERVICE_FUNCTION_PREFIX,
                "-", table_name)
        return function_name


class lambda_service(object):
    common_utils = CommonUtils()

    def put_data_entry(self, name, *args, **kwargs):
        '''create lambda function which pushes data to kinesis '''
        service_custom_name = kwargs.get('custom_name', None)
        function_name = self.common_utils.get_function_name(name,
                                                            service_custom_name)
        payload = args[0]
        logger.info("cdc_action : {0},"
                     "action_date : {1}," 
                     "lambda_name: {2}".format(payload.get('cdc_action'),
                                          payload.get('action_date'),
                                            function_name))

        payload_json = json.dumps(args, cls=PythonObjectEncoder)
        try:
            lambda_client.invoke(FunctionName=function_name,
                                 InvocationType='Event',
                                 Payload=payload_json)

        except Exception as e:
            logger.error("Error Occured while invoking lambda"
                         " function %s" % str(e))

    def get_serverless_func(self, lambda_name):
        function_val = {'name': lambda_name,
                        'handler': 'handler.push_data_to_kinesis',
                        'environment': {
                            'KINESIS_STREAM': lambda_name,
                            'AWS_REGION_NAME': settings.AWS_REGION_NAME}}
        return function_val


class kinesis_service(object):
    '''publish data directly on kinesis'''
    common_utils = CommonUtils()

    def put_data_entry(self, name, *args, **kwargs):
        try:
            service_custom_name = kwargs.get('custom_name', None)
            kinesis_stream = self.common_utils.get_function_name(name,
                                                                 service_custom_name)
            records = []
            payload = args[0]
            logger.info("cdc_action : {0},"
                         "action_date : {1},"
                         "kinesis_stream: {2}".format(payload.get('cdc_action'),
                                                payload.get('action_date'),
                                                kinesis_stream))
            for package in args:
                record = {
                    'Data': json.dumps(package, cls=PythonObjectEncoder),
                    'PartitionKey': str(uuid.uuid4())}
                records.append(record)
            response = kinesis_client.put_records(Records=records,
                                                  StreamName=kinesis_stream)
        except Exception as e:
            logger.error(
                "Error Occurred while pushing data to kinesis %s" % str(e))


class SNS_service(object):
    '''publish data directly on sns'''
    common_utils = CommonUtils()

    def put_data_entry(self, name, *args, **kwargs):
        try:
            payload = args[0]
            service_custom_name = kwargs.get('custom_name', None)
            function_name = self.common_utils.get_function_name(name,
                                                                service_custom_name)
            logger.info("cdc_action : {0},"
                         "action_date : {1},"
                         "sns_topic_name: {2}".format(payload.get('cdc_action'),
                                                payload.get('action_date'),
                                                function_name))
            arn = "{0}{1}".format(sns_arn, function_name)

            sns_client.publish(TargetArn=arn,
                               Message=json.dumps({
                                   'default':
                                       json.dumps(args,
                                                  cls=PythonObjectEncoder)
                               }),
                               MessageStructure='json')

        except ClientError as e:
            # if topic does not exist
            if e.response['Error']['Code'] == SNS_NOTFOUND_CODE and \
                    e.response['Error'][
                        'Message'] == SNS_TOPIC_NOT_EXIST_MESSAGE:
                sns_response = sns_client.create_topic(
                    Name=function_name
                )
                sns_client.publish(TargetArn=arn,
                                   Message=json.dumps({
                                       'default':
                                           json.dumps(args,
                                                      cls=PythonObjectEncoder)
                                   }),
                                   MessageStructure='json')
            # if error other than topic does not exist
            else:
                logger.error(
                    "Error Occurred while pushing data to SNS %s" % str(e))

        except Exception as e:
            logger.error(
                "Error Occurred while pushing data to SNS %s" % str(e))


class KafkaBase(CommonUtils):
    '''publish data directly on kafka'''

    def __get_hash_key(self, partition_key):
        return hashlib.md5(partition_key).hexdigest()[:9]

    def put_data_entry(self, name, *args, **kwargs):
        """
        :param name:
        :param args: [payload, partition_key]
        :param kwargs:
        :return:
        """
        partition_key = None
        hashed_partition_key = None
        try:
            service_custom_name = kwargs.get('custom_name', None)
            topic_name = self.get_function_name(name, service_custom_name)
            payload = args[0]
            logger.info("cdc_action : {0},"
                        "action_date : {1},"
                        "kafka_topic_name: {2}".format(payload.get('cdc_action'),
                                                     payload.get('action_date'),
                                                       topic_name))
            json_string = json.dumps(payload,
                                     ensure_ascii=False,
                                     cls=PythonObjectEncoder).encode('utf8')
            if len(args) > 1:
                partition_key = reduce(dict.__getitem__, args[1].split('.'),
                                       payload)
                hashed_partition_key = self.__get_hash_key(str(partition_key))

            try:
                kafka_producer_client.produce(topic_name,
                                              value=json_string,
                                              key=hashed_partition_key)
            except BufferError as e:
                kafka_producer_client.flush()
                logger.info("Reproduce Data for PartitionKey:{}".
                            format(partition_key))
                kafka_producer_client.produce(topic_name,
                                    value=json_string,
                                    key=hashed_partition_key)
            logger.info("KafkaResponse "
                        "partition key : {0}, "
                        "actual key : {1},"
                        "kafka_topic_name : {2},"
                        "cdc_action : {3}, "
                        "action_date : {4}".format(hashed_partition_key,
                                                   partition_key, topic_name,
                                                payload.get('cdc_action'),
                                                payload.get('action_date')))
        except Exception as e:
            logger.error("KafkaError:{0} "
                         "PartitionKey: {1},".format(str(e), partition_key))


class AsyncKafka_Service(KafkaBase):
    pass


class SyncKafka_Service(KafkaBase):
    def put_data_entry(self,name, *args, **kwargs):
        super(SyncKafka_Service, self).put_data_entry(name,*args,**kwargs)
        kafka_producer_client.flush()
