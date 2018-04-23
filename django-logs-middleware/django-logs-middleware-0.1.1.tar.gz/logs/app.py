import json
import traceback
from datetime import datetime

from django.conf import settings

from logs.engine import Engine


class Log:
    """
        A Log instances represents an even veing logged.

        Log instances are crated e
    """

    # -----------------------
    # Log source
    # -----------------------
    RESOURCE = 1
    MESSAGE = 2

    _source2Name = {
        RESOURCE: 'resource',
        MESSAGE: 'message'
    }

    # -----------------------
    # Log severity
    # -----------------------

    INFO = 1
    WARN = 5
    ERROR = 10

    _severity2Name = {
        INFO: 'INFO',
        WARN: 'WARNING',
        ERROR: 'ERROR'
    }

    _config_development = {
        'HOST': 'localhost',
        'PORT': 27017,
        'USER': None,
        'PASSWORD': None,
        'DATABASE': 'general',
        'COLLECTION': 'general'
    }

    _config_testing = {
        'HOST': '10.232.6.1',
        'PORT': 27017,
        'USER': None,
        'PASSWORD': None,
        'DATABASE': 'airbit_db',
        'COLLECTION': 'airbit_db'
    }

    environment = None
    only_errors = False
    config = None

    _config = {
        'development': _config_development,
        'testing': _config_testing
    }

    def __init__(self, environment=None):
        self.database = None
        self._set_types_log_save()
        self._set_environment(environment)
        self._make_config()

    def info(self, message):
        """
            Log a message with severity 'INFO' in the key severity and value 'MESSAGE' in the key 'resource'
            of the document to save.
        """
        self._log(severity=self.INFO, source=self.MESSAGE, msg=message)

    def warning(self, message):
        """
            Log a message with severity 'WARNING' in the key severity and value 'MESSAGE' in the key 'resource'
            of the document to save.
        """
        self._log(severity=self.WARN, source=self.MESSAGE, msg=message)

    def exception(self, message=None, exception=None):
        """
            Log a message with severity 'ERROR' in the key severity and value 'MESSAGE' in the key 'resource'
            of the document to save.
        """
        exception_data = {'exception': self._format_exception(exception)}
        self._log(severity=self.ERROR, source=self.MESSAGE, msg=message, exception_data=exception_data)

    def info_rsc(self, message=None, request=None, response=None):
        """
            Log a message with severity 'INFO' in the key severity and value 'RESOURCE' in the key 'resource'
            of the document to save.
        """
        self._log(severity=self.INFO, source=self.RESOURCE, msg=message, request=request, response=response)

    def warning_rsc(self, message=None, request=None, response=None):
        """
            Log a message with severity 'WARNING' in the key severity and value 'RESOURCE' in the key 'resource'
            of the document to save.
        """
        self._log(severity=self.WARN, source=self.RESOURCE, msg=message, request=request, response=response)

    def exception_rsc(self, message=None, request=None, response=None, exception=None, exception_ms=None):
        """
            Log a message with severity 'ERROR' in the key severity and value 'RESOURCE' in the key 'resource'
            of the document to save.
        """
        exception_data = {}
        if exception and not exception_ms:
            exception_data.update({'exception': self._format_exception(exception)})

        if exception_ms:
            exception_data.update(exception_ms)

        self._log(severity=self.ERROR, source=self.RESOURCE, msg=message, request=request, response=response,
                  exception_data=exception_data)

    def _log(self, severity, source, request=None, response=None, msg=None, exception_data=None):
        if self._save_log_type(severity=severity):
            data = self._format_header(source=source, severity=severity)

            msg = self._message(msg=msg, request=request, exception_data=exception_data)
            if msg:
                data.update({'message': msg})

            resource_data = self._format_resource(request=request, response=response)
            if resource_data:
                data.update({'resource': resource_data})

            request_data = self._format_request(request=request)
            if request_data:
                data.update({'request': request_data})

            response_result = self._format_response(response=response)
            if response_result:
                data.update({'response': response_result})

            if exception_data:
                data.update(exception_data)

            data = {'data': data}

            self._engine().insert_registry(data)

    def _save_log_type(self, severity):
        """
            Check if it only save the log severity type ERROR
        """
        if self.only_errors:
            print(severity)
            if severity == self.ERROR:
                return True
            else:
                return False
        else:
            return True

    @staticmethod
    def _message(msg, request, exception_data):
        """
            Set a default message if it nos passing to the logs
        """
        if not msg:
            if request and exception_data:
                msg = 'A exception is generated in the flow of the request'

            if exception_data and not request:
                msg = 'A exception is generated before to the flow of the request'

        return msg

    def _format_header(self, source, severity):
        """
            Create a dictionary with the primary information to save in the logs
        """
        data = {
            'created_at': str(datetime.utcnow()),
            'source': self._source2Name[source],
            'severity': self._severity2Name[severity],
        }

        app_name = self._get_app_name()
        if app_name:
            data.update({'app': app_name})

        return data

    @staticmethod
    def _get_app_name():
        """
        :return: the application name if exist the key APP_NAME in the settings.py file
        """
        if settings.APP_NAME:
            return settings.APP_NAME
        return None

    @staticmethod
    def _format_request(request):
        """
            Create a dictionary with the relevant information from the request
        """
        if not request:
            return None

        data = {
            'content_type': str(request.content_type),
            'headers': str(request.content_params)
        }

        if type(request.body) is dict:
            data.update({'body': json.loads(request.body).decode('utf-8')})

        if type(request.body) is bytes:
            data.update({'body': request.body.decode('utf-8')})

        return data

    @staticmethod
    def _format_response(response):
        """
            Create a dictionary with the relevant information from the response
        """
        if not response:
            return None
        data = {}

        if type(response.content) is dict:
            data.update({'body': str(json.loads(response.content).decode('utf-8'))})

        if type(response.content) is bytes:
            data.update({'body': str(response.content)})

        return data

    @staticmethod
    def _format_resource(request=None, response=None):
        """
            Create a dictionary who contains a resume of the result of the request and response
        """
        if not request and not response:
            return None

        data = {}

        if request:
            data.update({
                'method': str(request.method),
                'path': str(request.path),
                'full_path': str(request.get_full_path())
            })

        if response:
            data.update({
                'http_code': response.status_code
            })
        return data

    @staticmethod
    def _format_exception(exception):
        """
            Create a dictionary with the priority information of the exception generated
        :param exception:
        :return:
        """
        if not exception:
            return None
        type_ = type(exception).__name__
        traceback_ = traceback.format_exc()
        return {'type': type_, 'traceback': traceback_}

    def _set_types_log_save(self):
        """
            Verify if it only saves the log severity type ERROR
        """
        if settings.LOGS:
            for k, v in settings.LOGS.items():
                if str(k).upper() == 'only_errors'.upper():
                    print(v)
                    self.only_errors = v
                    break

    def _set_environment(self, environment=None):
        """
            set the environment type to use the configuration in the instance of the engine
        :param environment:
        :return:
        """
        if environment:
            self.environment = environment

        if not self.environment and settings.LOGS and isinstance(settings.LOGS, dict):
            for k, v in settings.LOGS.items():
                if str(k).upper() == 'environment'.upper():
                    self.environment = v
                    break

        if not self.environment:
            self.environment = 'development'

    def _make_config(self):
        """
            Get the environment to load de config settings to use in the instance of the database engine
        """
        if not self.config:
            for k, v in self._config.items():
                if str(k).upper() == self.environment.upper():
                    self.config = v

        temp_config = {}
        if settings.LOGS and isinstance(settings.LOGS, dict):
            for k, v in settings.LOGS.items():
                if str(k).upper() == self.environment.upper():
                    temp_config = v
                    break

        if temp_config and len(temp_config) > 0 and self.config:
            self.config.update(temp_config)

        if not self.config:
            self.config = temp_config.copy()

        if not self.config:
            self.config = self._config['development']

    @property
    def _instance_database(self):
        """
             Create a object of type Engine who has the settings of the database to connect and  save the log
        """
        host = self.config['HOST']
        port = self.config['PORT']

        user = self.config['USER']
        authentication = self.config['PASSWORD']
        database = self.config['DATABASE']
        collection = self.config['COLLECTION']
        return Engine(host=host, port=port, user=user, auth=authentication, database=database,
                      collection=collection)

    def _engine(self):
        """
        :return: the instances of the engine if it not exist generates a new one
        """
        if not self.database:
            self.database = self._instance_database
        return self.database
