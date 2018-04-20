# epanet toolkit
import json

import numpy as np
import pandas as pd
from epanettools.epanet2 import *
from epanettools.epanettools import *
from plotly import tools
from plotly.graph_objs import *
# plotting imports
from plotly.offline import plot


# extending the EPANetSimulation class to ease acces to
# simulation routines
class ENSim(EPANetSimulation):
    EN_INIT = 10

    def __init__(self, network_file, pdd=False):
        self.json_sim = {}
        super().__init__(network_file, pdd)

    def set_emitter(self, node_index, emitter_val):
        self.ENsetnodevalue(node_index, EN_EMITTER, emitter_val)

    def set_emitters(self, emitter_info=None):

        if emitter_info is None:
            # if arg is none reset emitter values
            for node_index in self.network.nodes:
                self.ENsetnodevalue(node_index, EN_EMITTER, 0)
        else:

            for node_index, emitter_val in emitter_info:
                self.set_emitter(node_index, emitter_val)

    def get_nodes_data(self, data_query, emitter=(1, 0)):

        no_nodes = ENSim._getncheck(self.ENgetcount(EN_NODECOUNT)) - ENSim._getncheck(self.ENgetcount(EN_TANKCOUNT))
        t_step = 1
        node_values = {}

        for queries in data_query:
            node_values[queries] = [[] for _ in range(no_nodes)]

        node_values["EMITTER_NODE"] = emitter[0]
        node_values["EMITTER_VAL"] = emitter[1]

        # initialize network for hydraulic process

        ENSim._getncheck(self.ENinitH(ENSim.EN_INIT))

        while t_step > 0:

            self.ENrunH()

            for node_index in range(1, no_nodes + 1):
                for query_type in data_query:
                    ret_val = ENSim._getncheck(self.ENgetnodevalue(node_index, eval(query_type)))
                    node_values[query_type][node_index - 1].append(ret_val)

            t_step = ENSim._getncheck(self.ENnextH())

        for key in node_values:
            node_values[key] = np.transpose(node_values[key]).tolist()

        return node_values

    def get_links_data(self, data_query, emitter=(1, 0)):

        no_links = self.ENgetcount(EN_LINKCOUNT)[1]
        t_step = 1
        link_values = {}

        for queries in data_query:
            link_values[queries] = [[] for _ in range(no_links)]

        link_values["EMITTER_NODE"] = emitter[0]
        link_values["EMITTER_VAL"] = emitter[1]

        while t_step > 0:
            ENSim._getncheck(self.ENrunH())

            for link_index in range(1, no_links + 1):
                for query_type in data_query:
                    ret_val = ENSim._getncheck(self.ENgetlinkvalue(link_index, eval(query_type)))
                    link_values[query_type][link_index - 1].append(ret_val)

            t_step = ENSim._getncheck(self.ENnextH())

        for key in link_values:
            link_values[key] = np.transpose(link_values[key]).tolist()

        return link_values

    def query_network(self, sim_dict):
        """
        :param sim_dict: a dict containing info about the network
        has the form
        {
            simulation_name : "name",
            simulation_type: "H" or "Q"
            emitter_values : [ (node_index, emitter_value) ]
            query : {
                nodes : [ "EN_PRESSURE"
                ]
                links : [ "EN_VELOCITY"
                ]
            }
        }
        :return: JSON with required data
        output_json format:
        {
            SIM_NAME = simulation-name
            NODE_VALUES = [
                {
                    "EN_PRESSURE" : [ [values for each node]]
                    "EMITTER_VAL" :
                    "EMITTER_NODE" :
                }
            ]

        }

        """

        # for the moment i'll treat only hydraulic simulations :)

        # initialize network simulaton

        ENSim._getncheck(self.ENopenH())

        # initialize session
        ENSim._getncheck(self.ENinitH(ENSim.EN_INIT))

        node_query = False
        link_query = False
        simulations = False

        # check json for querried data

        # node info:
        try:
            if sim_dict["query"]["nodes"]:
                node_query = True
        except KeyError:
            node_query = False

        # link info
        try:
            if sim_dict["query"]["links"]:
                link_query = True
        except KeyError:
            link_query = False

        # emitter info:
        try:
            simulations = sim_dict["emitter_values"]
        except KeyError:
            simulations = False

        if simulations:
            node_values = []
            link_values = []

            for node_index, emitter_value in simulations:
                print("Simulating emitter in node no{}".format(node_index))

                self.set_emitter(node_index, emitter_value)

                if node_query:
                    node_values.append(
                        self.get_nodes_data(sim_dict["query"]["nodes"], emitter=(node_index, emitter_value)))

                if link_query:
                    link_values.append(
                        self.get_links_data(sim_dict["query"]["links"], emitter=(node_index, emitter_value)))

                # reset emitter values everywhere in network
                self.set_emitters()

        else:

            if node_query:
                node_values = [self.get_nodes_data(sim_dict["query"]["nodes"])]
            else:
                node_values = []

            if link_query:
                link_values = [self.get_links_data(sim_dict["query"]["links"])]
            else:
                link_values = []

        self.ENcloseH()
        self.ENclose()

        self.__init__(self.OriginalInputFileName)
        self.json_sim = {
            "SIM_NAME": sim_dict["simulation_name"],
            "NODE_VALUES": node_values,
            "LINK_VALUES": link_values
        }
        return self.json_sim

    def get_time_step(self, pattern_id=1):
        """
        returns the time_step of the network in minutes
        :param pattern_id:
        :return:
        """
        return (24 * 60) / ENSim._getncheck(self.ENgetpatternlen(pattern_id))

    def plot(self, json_data):
        """
        utility function used to plot data from network simulations
        WIP
        :param json_data:
        :return:
        """

        values = json_data["NODE_VALUES"]
        date_range = pd.date_range('1/1/2018', periods=97, freq='15min')
        data1 = np.transpose(values[0]["EN_PRESSURE"])
        data2 = np.transpose(values[1]["EN_PRESSURE"])

        fig = tools.make_subplots(1, 2, subplot_titles=('Emitter Value = 0', 'Emitter Value = 760'))

        time_step = self.get_time_step()

        trace = []
        for vals in data1:
            fig.append_trace(Scatter(
                x=date_range,
                y=vals), 1, 1)

            trace.append(Scatter(
                x=date_range,
                y=vals))

        for vals in data2:
            fig.append_trace(Scatter(
                x=date_range,
                y=vals), 1, 2)

        fig['layout'].update(title='Pressure in water network')

        plot(fig)
        plot(trace)

    def save_data(self, path=None):

        try:
            with open(path, "wt") as file:
                file.write(json.dumps(self.json_sim))
        except IOError:
            print("Could not write to file {}".format(path))

    @staticmethod
    def write_json(output_json):

        json_data = json.dumps(output_json)
        with open("data.json", "wt") as f:
            f.write(json_data)

    @staticmethod
    def _getncheck(ret_val):

        # check the return code
        if isinstance(ret_val, list):
            if ret_val[0] == 0:
                # everything OK
                return ret_val[1]
            else:
                err_msg = ENgeterror(ret_val[0], 100)
                raise EpanetError(err_msg)
        else:
            if ret_val is not 0:
                err_msg = ENgeterror(ret_val, 100)
                raise EpanetError(err_msg)


def en_check(func):
    def func_wrapper(*args):
        ret_val = func(args)

        # check the return code
        if isinstance(ret_val, list):
            if ret_val[0] == 0:
                # everything OK
                return ret_val[1]
            else:
                err_msg = ENgeterror(ret_val[0], 100)
                raise EpanetError(err_msg)
        else:
            if ret_val is not 0:
                err_msg = ENgeterror(ret_val, 100)
                raise EpanetError(err_msg)


class EpanetError(Exception):

    def __init__(self, err_msg):
        super().__init__(err_msg)


if __name__ == '__main__':
    es = ENSim("data/hanoi.inp")

    emitters = [(5, 0),
                (5, 10),
                (5, 100),
                (10, 10),
                (10, 200)]

    query_dict = {
        "simulation_name": "Hanoi simulation",
        "simulation_type": "H",
        "emitter_values": emitters,
        "query": {

            "nodes": ["EN_PRESSURE", "EN_DEMAND"],
            "links": ["EN_VELOCITY"]
        }

    }

    data = es.query_network(query_dict)
    es.plot(data)
    es.save_data("emitter_simulations.json")
