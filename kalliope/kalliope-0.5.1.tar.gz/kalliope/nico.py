# coding: utf8
import logging

logging.basicConfig()
logger = logging.getLogger("kalliope")
logger.setLevel(logging.DEBUG)
from kalliope import BrainLoader, SettingLoader

brain = BrainLoader().brain
settings = SettingLoader().settings
# #
# order = "bla is my test"
# # order = "remind me to call mom in three seconds"
# SynapseLauncher.run_matching_synapse_from_order(order_to_process=order,
#                                                 brain=brain,
#                                                 settings=settings)

from kalliope.neurons.brain.brain import Brain as Brain_neuron

parameters = {
    'synapse_name': "say-hello-fr",
    'enabled': True
}

brain_neuron = Brain_neuron(**parameters)





