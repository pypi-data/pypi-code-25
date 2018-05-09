import configparser
import csv
import os
import network_metrics
import networkx as nx
from sklearn import linear_model, preprocessing
import numpy as np

class ExtractionNetwork():
    """
    """

    def __init__(self, input_file_paths, configuration_file = None, temp_dir_path = None):
        self.input_file_paths = input_file_paths
        self.configuration_file = configuration_file
        self.network_metrics_list = ['Order',
        'Gamma', 
        'Number_of_Connected_Components', 
        'Clustering_Coefficient',
        'Degree_Correlation',
        'Order_of_Largest_Connected_Component',
        'Algebraic_Connectivity_of_Largest_Connected_Component',
        'Vertex_Connectivity_of_Largest_Connected_Component',
        'Edge_Connectivity_of_Largest_Connected_Component',
        'Diameter_of_Largest_Connected_Component',
        'Average_Shortest_Path_of_Largest_Connected_Component']
        self.metric_results = dict()
        self.metric_weights = [-0.5, 0, 1, 0.8, 0, -0.8, 0, 0.7, 0.7, 0, 0]

        self.load_configurations()
        # Override
        if temp_dir_path:
            self.temp_dir_path = temp_dir_path



    def load_configurations(self):
        self.configurations = dict()
        self.configurations['metrics'] = dict()
        if self.configuration_file:
            config = configparser.RawConfigParser()
            config.read(self.configuration_file)
            self.configurations['temp_dir_path'] = config.get('General', 'temp_dir_path')
            self.configurations['metrics'][self.network_metrics_list[0]] = config.getboolean('Network_Metrics', self.network_metrics_list[0])
            self.configurations['metrics'][self.network_metrics_list[1]] = config.getboolean('Network_Metrics', self.network_metrics_list[1])
            self.configurations['metrics'][self.network_metrics_list[2]] = config.getboolean('Network_Metrics', self.network_metrics_list[2])
            self.configurations['metrics'][self.network_metrics_list[3]] = config.getboolean('Network_Metrics', self.network_metrics_list[3])
            self.configurations['metrics'][self.network_metrics_list[4]] = config.getboolean('Network_Metrics', self.network_metrics_list[4])
            self.configurations['metrics'][self.network_metrics_list[5]] = config.getboolean('Network_Metrics', self.network_metrics_list[5])
            self.configurations['metrics'][self.network_metrics_list[6]] = config.getboolean('Network_Metrics', self.network_metrics_list[6])
            self.configurations['metrics'][self.network_metrics_list[7]] = config.getboolean('Network_Metrics', self.network_metrics_list[7])
            self.configurations['metrics'][self.network_metrics_list[8]] = config.getboolean('Network_Metrics', self.network_metrics_list[8])
            self.configurations['metrics'][self.network_metrics_list[9]] = config.getboolean('Network_Metrics', self.network_metrics_list[9])
            self.configurations['metrics'][self.network_metrics_list[10]] = config.getboolean('Network_Metrics', self.network_metrics_list[10])
        else:
            self.configurations['temp_dir_path'] = None
            self.configurations['metrics'][self.network_metrics_list[0]] = True
            self.configurations['metrics'][self.network_metrics_list[1]] = True
            self.configurations['metrics'][self.network_metrics_list[2]] = True
            self.configurations['metrics'][self.network_metrics_list[3]] = False
            self.configurations['metrics'][self.network_metrics_list[4]] = True
            self.configurations['metrics'][self.network_metrics_list[5]] = True
            self.configurations['metrics'][self.network_metrics_list[6]] = False
            self.configurations['metrics'][self.network_metrics_list[7]] = False
            self.configurations['metrics'][self.network_metrics_list[8]] = False
            self.configurations['metrics'][self.network_metrics_list[9]] = False
            self.configurations['metrics'][self.network_metrics_list[10]] = False

    def _load_input(self, input_file_path):
        data_dict = dict() 
        with open(input_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for index, row in enumerate(reader):
                doc_id = row[0]
                extractions = list(row[1:])
                data_dict[doc_id] = extractions

        return data_dict

    def _get_dict_extraction_to_docid(self, extractions_dict):
        extraction_to_docid = dict()
        node_id = 0
        for doc, extractions in extractions_dict.items():
            for extraction in extractions:
                if extraction in extraction_to_docid:
                    extraction_to_docid[extraction].append(node_id)
                else:
                    extraction_to_docid[extraction] = [node_id]
            node_id += 1
        return extraction_to_docid

    def _convert_to_docs_network_adj_list(self, extraction_to_docid):
        adjacency_list = dict()
        for key, value in extraction_to_docid.items():
            for page1 in value:
                for page2 in value: 
                    if page1 != page2:
                        if page1 in adjacency_list:
                            adjacency_list[page1].add(page2)
                        else:
                            adjacency_list[page1] = set()
                            adjacency_list[page1].add(page2)

        return adjacency_list

    def _write_adj_list_to_file(self, adjacency_list, file_name, temp_dir_path):
        if not os.path.exists(temp_dir_path):
            os.makedirs(temp_dir_path)

        adj_file_complete = os.path.join(temp_dir_path, file_name)
        print("Writing "+adj_file_complete)
        with open(adj_file_complete, 'w') as f:
            for key, values in adjacency_list.items():
                f.write(str(key)+" ")
                for value in values:
                    f.write(str(value)+" ")
                f.write("\n")

    def get_metrics_from_files(self):
        self.input_file_names = list()
        for file_path in self.input_file_paths:
            print("Processing", file_path)
            file_name = os.path.basename(file_path)
            self.input_file_names.append(file_name)
            file_name_adj =file_name + '.adj'
            
            extractions_dict = self._load_input(file_path)
            extraction_to_docid = self._get_dict_extraction_to_docid(extractions_dict)
            adjacency_list = self._convert_to_docs_network_adj_list(extraction_to_docid)

            if self.configurations['temp_dir_path']:
                self._write_adj_list_to_file(adjacency_list, file_name_adj, self.configurations['temp_dir_path'])

            G = nx.from_dict_of_lists(adjacency_list)
            metric_results = self.single_point_network_metrics(G)
            self.metric_results[file_name] = metric_results
        return self.metric_results

    # def create_network(self):
    def single_point_network_metrics(self, G):
        print("Getting Single Point Network Metrics")
        return network_metrics.get_network_metrics(G, self.network_metrics_list, self.configurations['metrics'])
    
    def _get_train_data_from_resources(self):
        TRAIN_DATA_PATH = '../resources/train_data.csv'
        with open(TRAIN_DATA_PATH, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for index, row in enumerate(reader):
                doc_id = row[0]
                extractions = list(row[1:])
                data_dict[doc_id] = extractions

    def compare_networks(self):
        X = list()
        w = list()
        for index, metric in enumerate(self.network_metrics_list):
            if self.metric_weights[index] != 0:
                if self.configurations['metrics'][metric]:
                    print("Using ", metric)
                    metric_values = list()
                    for file_name in self.input_file_names:
                        metric_values.append(self.metric_results[file_name][metric])
                    X.append(metric_values)
                    w.append(self.metric_weights[index])
                else:
                    print("Skipping", metric, "for comparison as not calculated. Add to configurations for calculation.")

        print(X)
        X = preprocessing.normalize(X, norm='l2')
        # print(X)
        outputs = self.calculate_weights(X, w)
        prediction = self.input_file_names[list(outputs).index(max(outputs))]
        print("Network which is better:",prediction)

        return prediction, list(zip(self.input_file_names, outputs))

    def calculate_weights(self, X, w):
        X = np.array(X)
        w = np.array(w)
        print(X)
        print(w)
        output = np.matmul(X.transpose(), w)
        print(output)
        return output

    def predict_accuracy_of_extractions(self):
        regr = linear_model.LinearRegression()
        _get_train_data_from_resources()
        regr.fit(X_train, y_train) # Get from resources
        y_pred = regr.predict(X_test)
        # Predict for all values
        # Return which is better

    # def complete_analysis(self):


if __name__ == '__main__':
    print("Starting Extraction Network")
    input_file_paths = ['../resources/sample_extractions_data.csv', '../resources/sample_extractions_data_1.csv']
    extraction_network = ExtractionNetwork(input_file_paths, '../resources/sample_config_all.ini')
    metric_results = extraction_network.get_metrics_from_files()
    prediction, comparison = extraction_network.compare_networks()
    print(prediction, comparison)

