import os, sys
# from typing import NamedTuple, Union, List, Sequence, Any, Dict
import typing
from typing import Optional
from typing import Union
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

__all__ = ('JMI_Selector',)

class Params(params.Params):
    n_components_: Optional[int]


class Hyperparams(hyperparams.Hyperparams):

    n_components = hyperparams.Hyperparameter[Union[int, None]](
            default=None,
            description='Number of components to keep. if n_components is not set, all compoenents are kept'
    )



class JMI_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': '9d1a2e58-5f97-386c-babd-5a9b4e9b6d6c',
        'version': '2.1.4',
        'name': 'JMI feature selector',
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
        'python_path': 'd3m.primitives.rpi_featureSelection.IPCMBplus_Selector',
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
        self._n_components = self.hyperparams['n_components']
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
        
        if self._n_components:
            index = JMI_function(self._training_inputs, self._training_outputs, self._n_components)
        else:
            print(self._training_inputs.shape[1])
            index = JMI_function(self._training_inputs, self._training_outputs, self._training_inputs.shape[1])

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
	    n_components_ = getattr(self._n_components, 'n_components_', None)
	)

    def set_params(self, *, params:Params) -> None:
        self._n_components = params['n_components_']
        self._fitted = False



