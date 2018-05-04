import os, sys
# from typing import NamedTuple, Union, List, Sequence, Any, Dict
import typing
from typing import Optional
import scipy.io
import numpy as np

from d3m import container
from d3m.metadata import base as metadata_base
from d3m.metadata import hyperparams
from d3m.metadata import params
from d3m.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
from d3m.primitive_interfaces import base
from d3m.primitive_interfaces.base import CallResult

from rpi_featureSelection.coreFunctions import*

Inputs = container.ndarray
Outputs = container.ndarray

__all__ = ('STMBplus_Selector',)

class Params(params.Params):
    mi_thres_: Optional[float]


class Hyperparams(hyperparams.Hyperparams):

    mi_thres = hyperparams.Hyperparameter[float](
            default=0.02,
            description='The mutual information threshold for independency, default is 0.02.'
    )



class STMBplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': '9d1a2e58-5f97-386c-babd-5a9b4e9b6d6c',
        'version': '2.1.4',
        'name': 'STMBplus feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_featureSelection',
	            'version': '0.0.1'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection.STMBplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._mi_thres = self.hyperparams['mi_thres']
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')
        
        index = STMBplus(self._training_inputs, self._training_outputs, self._mi_thres)

        self._index = index.astype(int)
        self._fitted = True

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs: 
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Fit/Produce not performed')


    def get_params(self) -> Params:
        if not self._fitted:
            raise ValueError('Fit/Produce not performed')
        return Params(
	    mi_thres_ = getattr(self._mi_thres, 'mi_thres_', None)
	)

    def set_params(self, *, params:Params) -> None:
        self._mi_thres = params['mi_thres_']
        self._fitted = False



