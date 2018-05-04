#!/usr/local/bin/python3
import requests
from .docker_image import DockerImage
from .json_utils import json_hash, json_pretty

class Job(object):
    """
    An IPTK job is stored like any other IPTK metadata. This is a convenience
    class to create an empty IPTK dataset and store the job definition inside.
    This class will make sure that the same dataset identifier is used for 
    equivalent jobs, thus implementing a simple cache algorithm. Docker image
    references will be resolved and converted to a digest-based format upon
    job creation.
    """
    def __init__(self, image_reference, command=None):
        super(Job, self).__init__()
        self.image = DockerImage(image_reference)
        self.command = command
        self.inputs = []

    def add_input_dataset(self, dataset_id, path="/input"):
        input = {
            "type": "dataset",
            "id": dataset_id,
            "path": path
        }
        self.inputs.append(input)
        
    def save(self, base_path):
        """
        Create a new dataset and store this job's definition inside the 
        metadata.
        """

    def to_json(self):
        return json_pretty(self.spec)
    
    @property
    def spec(self):
        spec = {
            "version": 3,
            "image": self.image.spec,
            "command": self.command,
            "inputs": self.inputs
        }
        return spec
        
    @property
    def identifier(self):
        return json_hash(self.spec)
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.identifier}>"
