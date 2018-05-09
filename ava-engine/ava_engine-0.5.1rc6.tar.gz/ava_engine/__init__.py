#!/usr/bin/env python
# -*- coding: utf-8 -*-
import grpc

from ava_engine.ava.engine_api_pb2 import StatusRequest
from ava_engine.ava.engine_api_pb2 import EnableFeatureArguments, EnableFeatureRequest, IsFeatureEnabledRequest
from ava_engine.ava.feature_classification_pb2 import ClassifyRequest, GetClassifyRequest
from ava_engine.ava.engine_core_pb2 import ENCODED, RAW

from ava_engine.ava.engine_core_pb2 import ImageItem
from ava_engine.ava.service_api_pb2_grpc import EngineApiDefStub, ClassificationApiDefStub


class _ClassificationFeature:
    def __init__(self, channel):
        self._channel = channel
        self._stub = ClassificationApiDefStub(self._channel)

    def detect(self, images, classes, dtype=ENCODED, image_shape=None):
        return self._stub.Detect(ClassifyRequest(
            images=images,
            classes=classes,
            dtype=dtype,
            image_shape=image_shape,
        ))

    def get_detect(self, id_):
        return self._stub.GetDetect(GetClassifyRequest(id=id_))


class AvaEngineClient:
    def __init__(self, host='localhost', port=50051):
        self._host = host
        self._port = port

        self._channel = grpc.insecure_channel('{host}:{port}'.format(host=host, port=port))
        self._engine_stub = EngineApiDefStub(self._channel)

        self._features = {
            'classification': _ClassificationFeature(self._channel),
        }

    @property
    def classification(self):
        return self._features['classification']

    def status(self):
        return self._engine_stub.Status(StatusRequest())

    def enable_feature(self, feature_type, feature_args=None):
        feature_args = feature_args or {}
        request = EnableFeatureRequest(
            type=feature_type,
            arguments=EnableFeatureArguments(
                classes=feature_args.get('classes', []),
                model_id=feature_args.get('model_id'),
                dtype=feature_args.get('dtype', feature_args.get('dtype')),
            ),
        )
        return self._engine_stub.EnableFeature(request)

    def is_feature_enabled(self, feature_type):
        return self._engine_stub.IsFeatureEnabled(IsFeatureEnabledRequest(type=feature_type))
