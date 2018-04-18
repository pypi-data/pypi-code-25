__author__ = 'Bohdan Mushkevych'

import os
import avro
import importlib
import importlib.util
from yaml import load as yaml_load, dump, YAMLObject

from schema.avro_schema import AvroSchema
from schema.protobuf_schema import ProtobufSchema

EXTENSION_AVRO = 'avsc'
EXTENSION_SDPL = 'yaml'
EXTENSION_PROTOBUF = 'proto'
MODEL_NAME_DELIMITER = '|'


def load(input_path:str):
    model_name = None
    if MODEL_NAME_DELIMITER in input_path:
        tokens = input_path.split(MODEL_NAME_DELIMITER, maxsplit=1)
        model_name = tokens[1]
        input_path = tokens[0]

    extension = os.path.basename(input_path).split('.')[-1]
    with open(input_path, mode='r', encoding='utf-8') as input_stream:
        if extension == EXTENSION_SDPL:
            return yaml_load(input_stream)
        elif extension == EXTENSION_AVRO:
            s = avro.schema.Parse(input_stream.read())
            return AvroSchema(s).to_sdpl_schema()
        elif extension == EXTENSION_PROTOBUF:
            if not model_name:
                raise ValueError('optional attribute model_name is required to parse .proto schema')

            input_path = input_path.replace('.proto', '_pb2.py')
            py_spec = importlib.util.spec_from_file_location(model_name, input_path)
            py_module = importlib.util.module_from_spec(py_spec)
            py_spec.loader.exec_module(py_module)
            s = getattr(py_module, model_name)
            return ProtobufSchema(s).to_sdpl_schema()
        else:
            raise ValueError('unknown schema file extension {0}'.format(extension))


def store(yaml_object:YAMLObject, output_path:str):
    output_path = output_path.strip('\'')
    with open(output_path, 'w', encoding='utf-8') as output_stream:
        dump(yaml_object, output_stream)
