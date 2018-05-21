import numpy as np
from .base import ActiveLearningModel


class RandomSampler(ActiveLearningModel):
    def __init__(self, seed=42):
        self.random = np.random.RandomState(seed)

    def get_confidence(self, examples):
        return self.random.rand(len(examples))

    def train(self, labeled_examples):
        pass

    def is_trained(self):
        return True

    def needs_serialized(self):
        return False
