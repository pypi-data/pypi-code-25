import atexit
import datetime
import functools
import hashlib
import logging
import os
import socket
import threading
import time
import traceback
import urllib2
from copy import deepcopy

import elasticsearch
import elasticsearch.helpers


class Constants:
	HOST_KEY = 'host'
	PROCESS_KEY = 'process'
	THREAD_NAME_KEY = 'threadName'
	THREAD_ID_KEY = 'thread'
	USERNAME_KEY = 'username'
	TIMESTAMP_KEY = 'timestamp'
	INFO_VALUE = 'INFO'
	WARN_VALUE = 'WARN'
	ERROR_VALUE = 'ERROR'
	LEVEL_NAME_KEY = 'levelname'
	FEATURE_NAME_KEY = 'feature_name'
	FEATURE_DURATION_KEY = 'feature_duration_seconds'


class RepeatingThread(threading._Timer):
	def run(self):
		while not self.finished.wait(self.interval) and self.finished.is_set():
			try:
				self.function(*self.args, **self.kwargs)
			except Exception as e:
				# keep going, and try again in the next time slot to push data
				pass


class ElasticSearchHelper(object):
	
	def __init__(self, client, index, extra_values=None, auto_flush=True, flush_period_seconds=1):
		"""
		
		:param client: ElasticSearch Client that's already initialized
		:param index: index name without wildcard (year and date will be automatically added, foo_index -> foo_index.year.month)
		:param extra_values: dictionary of extra values that will go with every request
		:param auto_flush: Whether or not
		:param flush_period_seconds: The frequency of flushing in seconds
		"""
		assert index.islower(), "index must be all lower-case. This is an ElasticSearch limitation"
		self.client = client
		self.index = index
		self.flush_thread = None
		if auto_flush:
			self.flush_thread = RepeatingThread(flush_period_seconds, self.flush_buffer)
		self.actions_buffer = []
		self.validate_connection()
		self.extra_values = extra_values or {}
		# make sure we flush when process exit
		atexit.register(self.on_process_exit)
	
	@classmethod
	def get_instance(cls, host, index, port=9200, use_ssl=False, verify_certs=True,
	                 connection_class=elasticsearch.RequestsHttpConnection,
	                 **kwargs):
		"""
		Factory method for easy construction
		:rtype: ElasticSearchHelper
		"""
		client = elasticsearch.Elasticsearch(hosts=[{'host': host, 'port': port}], use_ssl=use_ssl,
		                                     verify_certs=verify_certs,
		                                     connection_class=connection_class, **kwargs)
		return cls(client, index)
	
	def change_flush_interval(self, interval):
		"""
		Change flush interval of buffering thread
		:param interval: interval in seconds
		"""
		assert self.flush_thread, "Cannot change flush interval when auto_flush is False"
		self.flush_thread.interval = interval
	
	def on_process_exit(self):
		"""
		This will be called when process exit to flush remaining records if auto_flush is enabled
		:return: None
		"""
		if self.flush_thread:
			self.flush_thread.cancel()
			self.flush_buffer()
	
	def add_elasticsearch_records(self, data_list):
		"""
		add records to buffer. Will not be pushed to elasticsearch unless flush_buffer is called
		:param data_list: list of dict that contains data to be pushed, default_values will be automatically added to each dictionary
							each dict cannot contain duplicate keys with default_values
		:return: None
		"""
		actions = [self.create_data_record(data_dict) for data_dict in data_list]
		self.actions_buffer.extend(actions)
	
	def flush_buffer(self):
		"""
		Flush buffer and push it to elasticsearch
		:return: None
		"""
		if not self.actions_buffer:
			return
		
		# reset actions buffer and take what's currently in the list
		actions = self.actions_buffer
		self.actions_buffer = []
		try:
			elasticsearch.helpers.bulk(self.client, actions, stats_only=True)
		except Exception as e:
			# put actions back if it failed
			self.actions_buffer.extend(actions)
			raise
	
	def create_data_record(self, data_dict):
		"""
		Create data record (dict) that is ready to be pushed to elasticsearch
		:param data_dict:
		:return: dict of elastic search record
		:rtype: dict
		"""
		source_dict = deepcopy(data_dict)
		assert not self.is_conflicting_keys(data_dict,
		                                    self.default_values), "Conflicting keys between default_values and extra_values"
		source_dict.update(self.default_values)
		return {
			'_index' : self.get_full_index(),
			'_type'  : 'python_log',
			'_source': source_dict
		}
	
	@classmethod
	def is_conflicting_keys(cls, d1, d2):
		"""
		Return trur if there are conflicting keys between 2 dictionaries
		:param d1:
		:param d2:
		:return:
		"""
		return bool(set(d1.keys()).intersection(set(d2.keys())))
	
	def get_full_index(self):
		"""
		get index name
		:rtype: str
		:return: Index name with year and month attached to it
		"""
		datenow = datetime.datetime.utcnow()
		index = '{index}-{year}.{month}'.format(index=self.index, year=datenow.year, month=datenow.month)
		return index
	
	@property
	def default_values(self):
		data_dict = {
			Constants.HOST_KEY       : socket.getfqdn(),
			Constants.PROCESS_KEY    : os.getpid(),
			Constants.THREAD_NAME_KEY: threading.current_thread().name,
			Constants.THREAD_ID_KEY  : threading.current_thread().ident,
			Constants.TIMESTAMP_KEY  : str(datetime.datetime.utcnow().isoformat())
		}
		assert not self.is_conflicting_keys(data_dict,
		                                    self.extra_values), "Conflicting keys between default_values and extra_values"
		data_dict.update(self.extra_values)
		return data_dict
	
	def validate_connection(self):
		"""
		ping server to make sure it's reachable. Raises exception if server cannot be reached
		:return:
		"""
		for hostInfo in self.client.transport.hosts:
			host = hostInfo.get('host')
			port = hostInfo.get('port')
			self.validate_server_connection(host, port)
	
	@classmethod
	def validate_server_connection(cls, host, port):
		url = 'http://{}:{}'.format(host, port)
		urllib2.urlopen(url)
	
	def log_feature(self, feature_name, feature_duration_seconds=None, levelname=Constants.INFO_VALUE, **kwargs):
		"""
		log feature and it to buffer, this will not push data immediately to elastic search. Subsequent call to flush_buffer is required if auto_flush is disabled
		:param feature_name: feature name in string
		:param feature_duration_seconds: time it took to complete this feature in seconds
		:param levelname: Severity of this log (INFO, ERROR, WARN)
		:param kwargs: additional values to be added to the record
		:return:
		"""
		data_dict = {
			Constants.FEATURE_NAME_KEY: feature_name,
			Constants.LEVEL_NAME_KEY  : levelname,
		}
		data_dict.update(**kwargs)
		if feature_duration_seconds is not None:
			data_dict.update({Constants.FEATURE_DURATION_KEY: feature_duration_seconds})
		
		self.add_elasticsearch_records([data_dict])
	
	def log_feature_error(self, feature_name, feature_duration_seconds=None, **kwargs):
		"""
		Log feature as an error, Same as log_feature but with levelname = ERROR
		"""
		self.log_feature(feature_name, feature_duration_seconds=feature_duration_seconds,
		                 levelname=Constants.ERROR_VALUE, **kwargs)
	
	def log_feature_decorator(self, feature_name, **feature_kwargs):
		"""
		Decorator to be used on any function, without changing its behavior. Each call to the decorated function will add it to buffer
		:param feature_name: feature name in string
		:param feature_kwargs: Additional values that will be added to each function call
		:return:
		"""
		
		# create actual decorator, since this decorator take an argument of featureName
		def decorator(function):
			@functools.wraps(function)
			def wrapper(*args, **kwargs):
				start = time.time()
				# execute function
				try:
					return_val = function(*args, **kwargs)
					duration_seconds = time.time() - start
					try:
						self.log_feature(feature_name, duration_seconds, **feature_kwargs)
					except Exception as e:
						logging.debug("Couldn't log feature", exc_info=1)
					return return_val
				except Exception as e:
					exc_text = traceback.format_exc()
					duration_seconds = time.time() - start
					exc_hash = hashlib.sha1(exc_text).hexdigest()
					try:
						self.log_feature_error(feature_name, duration_seconds,
						                       exc_text=exc_text,
						                       exc_hash=exc_hash,
						                       exc_message=e.message,
						                       **feature_kwargs)
					except Exception as e:
						logging.debug("Couldn't log feature error", exc_info=1)
					raise
			
			return wrapper
		
		return decorator
