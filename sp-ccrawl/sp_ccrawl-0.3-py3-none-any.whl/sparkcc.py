import argparse
import logging
import os
import re

from tempfile import TemporaryFile

import boto3
import botocore

from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArchiveLoadFailed

from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from pyspark.sql.types import StructType, StructField, StringType, LongType
from conf import Conf
from pathlib import Path
import shutil


LOGGING_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'


class CCSparkJob:
    def __init__(self):
        self._name = self.__class__.__name__

        self._output_schema = StructType([
            StructField("key", StringType(), True),
            StructField("val", LongType(), True)
        ])

        self._warc_parse_http_header = True

        self._args = None
        self._records_processed = None
        self._warc_input_processed = None
        self._warc_input_failed = None
        self._log_level = 'WARN'
        self._conf = None
        logging.basicConfig(level=self._log_level, format=LOGGING_FORMAT)

        self._num_input_partitions = 400
        self._num_output_partitions = 10

    def parse_arguments(self):
        """ Returns the parsed arguments from the command line """

        descr = ('Find wet.path.gz files on Amazon for required dates, '
                 "download if no local copy found, restrict according to actual dates")
        parser = argparse.ArgumentParser(description=descr)
        parser.add_argument("--conf", "-c", required=True,
                            default='proj.conf',
                            help="path to a configuration file. Default is proj.conf")
        parser.add_argument("--verbose", "-v", default=False, action='store_true',
                            help="increase verbosity")
        pargs = parser.parse_args()
        VERBOSE = pargs.verbose
        print(pargs.conf, pargs.verbose)
        self._conf = Conf()
        print(pargs.conf)
        self._conf.read(pargs.conf)
        if VERBOSE:
            self._conf.process.log_level = "DEBUG"
        self._conf.finalize()
        self.validate_arguments()
        self.init_logging()

    def add_arguments(self, parser):
        pass

    def validate_arguments(self):
        return True

    def init_logging(self):
        logging.basicConfig(level=self._conf.process.log_level, format=LOGGING_FORMAT)

    def get_logger(self, spark_context=None):
        """Get logger from SparkContext or (if None) from logging module"""
        if spark_context is None:
            return logging.getLogger(self._name)
        return spark_context._jvm.org.apache.log4j.LogManager.getLogger(self._name)

    def run(self):
        self.parse_arguments()

        if self._conf.process.rewrite:
            shutil.rmtree(self._conf.process.local_temp_dir, ignore_errors=True)
        # Python3.4 on AWS doesn't have the 'exist_ok' option. Try ... catch is a replacement.
        try:
            Path(self._conf.process.local_temp_dir).mkdir(parents=True)
        except:
            pass

        spark_conf = SparkConf().setAll((
            ("spark.task.maxFailures", "10"),
            ("spark.locality.wait", "20s"),
            ("spark.serializer", "org.apache.spark.serializer.KryoSerializer"),
        ))
        sc = SparkContext(
            appName=self._name,
            conf=spark_conf)
        sqlc = SQLContext(sparkContext=sc)
        sc.setLogLevel(self._conf.process.log_level)

        self._records_processed = sc.accumulator(0)
        self._warc_input_processed = sc.accumulator(0)
        self._warc_input_failed = sc.accumulator(0)

        self.run_job(sc, sqlc)

        sc.stop()

    def log_aggregator(self, sc, agg, descr):
        self.get_logger(sc).info(descr.format(agg.value))

    def log_aggregators(self, sc):
        self.log_aggregator(sc, self._warc_input_processed,
                            'WARC input files processed = {}')
        self.log_aggregator(sc, self._warc_input_failed,
                            'records processed = {}')
        self.log_aggregator(sc, self._records_processed,
                            'records processed = {}')

    @staticmethod
    def reduce_by_key_func(a, b):
        return a + b

    def run_job(self, sc, sqlc):
        input_data = sc.textFile(self._conf.process.input,
                                       minPartitions=self._conf.process.num_input_partitions)

        output = input_data.mapPartitionsWithIndex(self.process_warcs) \
            .reduceByKey(self.reduce_by_key_func)

        sqlc.createDataFrame(output, schema=self._output_schema) \
            .coalesce(self._conf.process.num_output_partitions) \
            .write \
            .format("parquet") \
            .saveAsTable(self._conf.process.output)

        # self.log_aggregators(sc)
        self.get_logger(sc).info('records processed = {}'.format(
            self._records_processed.value))

    def process_warcs(self, id_, iterator):
        s3pattern = re.compile('^s3://([^/]+)/(.+)')
        base_dir = os.path.abspath(os.path.dirname(__file__))

        # S3 client (not thread-safe, initialize outside parallelized loop)
        no_sign_request = botocore.client.Config(
            signature_version=botocore.UNSIGNED)
        s3client = boto3.client('s3', config=no_sign_request)

        for uri in iterator:
            self._warc_input_processed.add(1)
            if self._conf.process.load_from_s3:
                if not uri.startswith('s3://'):
                    uri = self._conf.process.s3_prefix + uri
            self.get_logger().info("processing uri {}".format(uri))
            if uri.startswith('s3://'):
                self.get_logger().info('Reading from S3 {}'.format(uri))
                s3match = s3pattern.match(uri)
                if s3match is None:
                    self.get_logger().error("Invalid S3 URI: " + uri)
                    continue
                bucketname = s3match.group(1)
                path = s3match.group(2)
                warctemp = TemporaryFile(mode='w+b',
                                         dir=self._conf.process.local_temp_dir)
                try:
                    s3client.download_fileobj(bucketname, path, warctemp)
                except botocore.client.ClientError as exception:
                    self.get_logger().error(
                        'Failed to download {}: {}'.format(uri, exception))
                    self.warc_input_failed.add(1)
                    continue
                warctemp.seek(0)
                stream = warctemp
            elif uri.startswith('hdfs://'):
                self.get_logger().error("HDFS input not implemented: " + uri)
                continue
            else:
                self.get_logger().info('Reading local stream {}'.format(uri))
                if uri.startswith('file:'):
                    uri = uri[5:]
                uri = os.path.join(base_dir, uri)
                try:
                    stream = open(uri, 'rb')
                except IOError as exception:
                    self.get_logger().error(
                        'Failed to open {}: {}'.format(uri, exception))
                    self._warc_input_failed.add(1)
                    continue

            no_parse = (not self._warc_parse_http_header)
            try:
                for record in ArchiveIterator(stream, no_record_parse=no_parse):
                    for res in self.process_record(record):
                        yield res
                    self._records_processed.add(1)
            except ArchiveLoadFailed as exception:
                self._warc_input_failed.add(1)
                self.get_logger().error(
                    'Invalid WARC: {} - {}'.format(uri, exception))

    def process_record(self, record):
        raise NotImplementedError('Processing record needs to be customized')

    @staticmethod
    def is_wet_text_record(record):
        """Return true if WARC record is a WET text/plain record"""
        return (record.rec_type == 'conversion' and
                record.content_type == 'text/plain')

    @staticmethod
    def is_wat_json_record(record):
        """Return true if WARC record is a WAT record"""
        return (record.rec_type == 'metadata' and
                record.content_type == 'application/json')
